"""
animation — Tween + Spring + Animator singleton.

Usage:
    from pg_ui.animation import animator

    # Tween: interpolate a property from current value to `end` over duration
    animator.tween(target, 'alpha', 255, duration=0.2, easing='ease_out')

    # Spring: physics-based, iOS-feeling motion toward `end`
    animator.spring(target, 'scale', 1.0, stiffness=200, damping=22)

Main loop:
    animator.update(dt)   # call once per frame; no-op when no active anims.
"""


# ───── Easing functions ───────────────────────────────────────────

def linear(t):        return t
def ease_in(t):       return t * t
def ease_out(t):      return 1 - (1 - t) * (1 - t)
def ease_in_out(t):   return 3 * t * t - 2 * t * t * t
def ease_out_cubic(t): return 1 - (1 - t) ** 3
def ease_in_cubic(t): return t * t * t
def ease_out_expo(t): return 1 - 2 ** (-10 * t) if t < 1 else 1

EASINGS = {
    'linear':       linear,
    'ease_in':      ease_in,
    'ease_out':     ease_out,
    'ease_in_out':  ease_in_out,
    'ease_out_cubic': ease_out_cubic,
    'ease_in_cubic': ease_in_cubic,
    'ease_out_expo': ease_out_expo,
}


# ───── Tween ──────────────────────────────────────────────────────

class Tween:
    """Duration-based interpolation of a numeric or tuple property."""

    def __init__(self, target, prop, end, duration, easing='ease_out',
                 start=None, on_update=None, on_complete=None, delay=0.0):
        self.target = target
        self.prop = prop
        self.end = end
        self._start_snapshot = start  # None → captured lazily at first update
        self.duration = max(1e-6, float(duration))
        self.easing_fn = EASINGS.get(easing, ease_out) if isinstance(easing, str) else easing
        self.on_update = on_update
        self.on_complete = on_complete
        self.delay = delay
        self.elapsed = 0.0
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def update(self, dt):
        if self._cancelled:
            return True
        if self.delay > 0:
            self.delay -= dt
            if self.delay > 0:
                return False
        if self._start_snapshot is None:
            self._start_snapshot = getattr(self.target, self.prop)
        self.elapsed += dt
        t = min(1.0, self.elapsed / self.duration)
        eased = self.easing_fn(t)
        value = self._interp(self._start_snapshot, self.end, eased)
        setattr(self.target, self.prop, value)
        if self.on_update:
            self.on_update(value)
        if t >= 1.0:
            if self.on_complete:
                self.on_complete()
            return True
        return False

    @staticmethod
    def _interp(a, b, t):
        if isinstance(a, (int, float)):
            return a + (b - a) * t
        if isinstance(a, (tuple, list)):
            return type(a)(a[i] + (b[i] - a[i]) * t for i in range(len(a)))
        return b


# ───── Spring ─────────────────────────────────────────────────────

class Spring:
    """
    Spring-damped animation. Physics model (mass-spring-damper):
        F = -k (x - target) - c v
        a = F / m

    Defaults (k=180, c=22, m=1) give iOS-like critically-damped motion.
    Lower damping (c<20 @ k=180) introduces a slight bounce.
    """

    def __init__(self, target, prop, end, stiffness=180, damping=22,
                 mass=1.0, velocity=0, on_complete=None, epsilon=0.01):
        self.target = target
        self.prop = prop
        self.end = end
        self.k = stiffness
        self.c = damping
        self.m = mass
        self.value = getattr(target, prop)
        self._scalar = isinstance(self.value, (int, float))
        if self._scalar:
            self.velocity = float(velocity)
        else:
            self.velocity = tuple(float(velocity) for _ in self.value) if isinstance(velocity, (int, float)) else tuple(velocity)
        self.on_complete = on_complete
        self.epsilon = epsilon
        self._done = False
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def update(self, dt):
        if self._cancelled:
            return True
        # Clamp dt to avoid blow-ups on slow frames
        dt = min(dt, 1 / 30.0)

        if self._scalar:
            force = -self.k * (self.value - self.end) - self.c * self.velocity
            accel = force / self.m
            self.velocity += accel * dt
            self.value += self.velocity * dt
            if abs(self.velocity) < self.epsilon and abs(self.value - self.end) < self.epsilon:
                self.value = self.end
                self._done = True
        else:
            new_vals, new_vels = [], []
            all_done = True
            for v, e, vel in zip(self.value, self.end, self.velocity):
                force = -self.k * (v - e) - self.c * vel
                accel = force / self.m
                vel = vel + accel * dt
                v = v + vel * dt
                if abs(vel) >= self.epsilon or abs(v - e) >= self.epsilon:
                    all_done = False
                new_vals.append(v)
                new_vels.append(vel)
            self.value = type(self.end)(new_vals) if isinstance(self.end, (tuple, list)) else tuple(new_vals)
            self.velocity = tuple(new_vels)
            if all_done:
                self.value = self.end
                self._done = True

        setattr(self.target, self.prop, self.value)
        if self._done and self.on_complete:
            self.on_complete()
        return self._done


# ───── Sequence / Parallel helpers ────────────────────────────────

class Sequence:
    """Run animations one after another."""
    def __init__(self, *anims, on_complete=None):
        self.anims = list(anims)
        self.index = 0
        self.on_complete = on_complete
        self._cancelled = False

    def cancel(self): self._cancelled = True

    def update(self, dt):
        if self._cancelled:
            return True
        if self.index >= len(self.anims):
            if self.on_complete: self.on_complete()
            return True
        if self.anims[self.index].update(dt):
            self.index += 1
        if self.index >= len(self.anims):
            if self.on_complete: self.on_complete()
            return True
        return False


class Parallel:
    """Run animations together; completes when all finish."""
    def __init__(self, *anims, on_complete=None):
        self.anims = list(anims)
        self.on_complete = on_complete
        self._cancelled = False

    def cancel(self): self._cancelled = True

    def update(self, dt):
        if self._cancelled:
            return True
        self.anims = [a for a in self.anims if not a.update(dt)]
        if not self.anims:
            if self.on_complete: self.on_complete()
            return True
        return False


# ───── Animator (global) ──────────────────────────────────────────

class Animator:
    """
    Owns all active animations. App runner calls `update(dt)` each frame.
    When idle (`is_busy()` is False), update is effectively free.
    """

    def __init__(self):
        self._active = []

    def add(self, anim):
        self._active.append(anim)
        return anim

    def tween(self, target, prop, end, duration=0.25, easing='ease_out', **kw):
        return self.add(Tween(target, prop, end, duration, easing, **kw))

    def spring(self, target, prop, end, stiffness=180, damping=22, **kw):
        return self.add(Spring(target, prop, end, stiffness, damping, **kw))

    def sequence(self, *anims, **kw):
        return self.add(Sequence(*anims, **kw))

    def parallel(self, *anims, **kw):
        return self.add(Parallel(*anims, **kw))

    def update(self, dt):
        if not self._active:
            return
        self._active = [a for a in self._active if not a.update(dt)]

    def is_busy(self):
        return bool(self._active)

    def clear(self):
        self._active.clear()


animator = Animator()
