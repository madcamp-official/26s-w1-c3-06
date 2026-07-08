import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation
from collections import deque


# ----------------------------------------------------------------------
# Black-Scholes pricing and Greeks
# ----------------------------------------------------------------------

def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_pdf(x):
    return math.exp(-x * x / 2.0) / math.sqrt(2.0 * math.pi)


def black_scholes(S, K, T, r, sigma):
    """Return call/put price and Greeks for the given inputs.

    T is time to expiry in day. A tiny floor is applied to T to avoid
    division by zero as expiry is approached.
    """
    T = max(T, 1.0 / (86400.0 * 24.0))

    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    Nd1, Nd2 = norm_cdf(d1), norm_cdf(d2)
    Nnd1, Nnd2 = norm_cdf(-d1), norm_cdf(-d2)
    pdf1 = norm_pdf(d1)
    disc = math.exp(-r * T)

    call = S * Nd1 - K * disc * Nd2
    put = K * disc * Nnd2 - S * Nnd1

    gamma = pdf1 / (S * sigma * math.sqrt(T))
    vega = S * pdf1 * math.sqrt(T) / 100.0            # per 1% change in vol

    call_theta = (-(S * pdf1 * sigma) / (2 * math.sqrt(T)) - r * K * disc * Nd2) / 86400.0
    put_theta = (-(S * pdf1 * sigma) / (2 * math.sqrt(T)) + r * K * disc * Nnd2) / 86400.0

    call_rho = K * T * disc * Nd2 / 100.0             # per 1% change in rate
    put_rho = -K * T * disc * Nnd2 / 100.0

    return {
        "call": call, "put": put,
        "call_delta": Nd1, "put_delta": Nd1 - 1.0,
        "gamma": gamma, "vega": vega,
        "call_theta": call_theta, "put_theta": put_theta,
        "call_rho": call_rho, "put_rho": put_rho,
    }


# ----------------------------------------------------------------------
# GBM price simulator
# ----------------------------------------------------------------------

class GBMSimulator:
    def __init__(self, s0=100.0, mu=0.05, sigma=0.25, texp_secs=30, ticks_per_life=8640):
        self.s0 = s0
        self.mu = mu
        self.sigma = sigma
        self.texp_secs = texp_secs
        self.ticks_per_life = ticks_per_life
        self.rng = np.random.default_rng()
        self.reset()

    def reset(self):
        self.S = self.s0
        self.elapsed_day = 0.0
        self.expired = False
        self.history = deque([self.s0], maxlen=self.ticks_per_life)

    def total_day(self):
        return self.texp_secs / 86400.0

    def dt_day(self):
        return self.total_day() / self.ticks_per_life

    def step(self):
        if self.expired:
            return
        dt = self.dt_day()
        z = self.rng.standard_normal()
        drift = (self.mu - 0.5 * self.sigma ** 2) * dt
        shock = self.sigma * math.sqrt(dt) * z
        self.S = self.S * math.exp(drift + shock)
        self.elapsed_day += dt
        self.history.append(self.S)
        if self.elapsed_day >= self.total_day():
            self.expired = True

    def remaining_day(self):
        return max(0.0, self.total_day() - self.elapsed_day)


# ----------------------------------------------------------------------
# Live animation
# ----------------------------------------------------------------------

def main():
    sim = GBMSimulator(s0=100.0, mu=0.05, sigma=0.25, texp_secs=30)
    K0 = 100.0
    r0 = 0.04

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(11, 6.5))
    plt.subplots_adjust(bottom=0.34, top=0.88)

    line, = ax.plot([], [], color="#35D68C", linewidth=1.8)
    dot = ax.scatter([], [], color="#35D68C", s=30, zorder=5)
    strike_line = ax.axhline(K0, color="#E8A33D", linestyle="--", alpha=0.55, label="Strike K")

    ax.set_xlim(0, sim.ticks_per_life)
    ax.set_ylabel("Price ($)")
    ax.set_xlabel("Tick")
    ax.grid(alpha=0.15)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.2)

    title_text = fig.text(0.02, 0.955, "", fontsize=15, fontfamily="monospace", color="#35D68C")
    info_text = fig.text(0.02, 0.915, "", fontsize=10, fontfamily="monospace", color="#9AA6AD")
    call_text = fig.text(0.55, 0.955, "", fontsize=10, fontfamily="monospace", color="#35D68C")
    put_text = fig.text(0.55, 0.915, "", fontsize=10, fontfamily="monospace", color="#FF5D5D")

    state = {"running": True}

    # --- sliders ---
    slider_color = "#E8A33D"
    ax_mu = plt.axes([0.15, 0.22, 0.32, 0.03])
    ax_sigma = plt.axes([0.15, 0.17, 0.32, 0.03])
    ax_r = plt.axes([0.15, 0.12, 0.32, 0.03])
    ax_k = plt.axes([0.15, 0.07, 0.32, 0.03])

    s_mu = Slider(ax_mu, "mu (drift)", -0.30, 0.30, valinit=sim.mu, color=slider_color)
    s_sigma = Slider(ax_sigma, "sigma (vol)", 0.01, 1.00, valinit=sim.sigma, color=slider_color)
    s_r = Slider(ax_r, "r (rate)", 0.00, 0.15, valinit=r0, color=slider_color)
    s_k = Slider(ax_k, "K (strike)", 10.0, 300.0, valinit=K0, color=slider_color)

    params = {"r": r0, "K": K0}

    def on_slider_change(_):
        sim.mu = s_mu.val
        sim.sigma = s_sigma.val
        params["r"] = s_r.val
        params["K"] = s_k.val
        strike_line.set_ydata([params["K"], params["K"]])

    for s in (s_mu, s_sigma, s_r, s_k):
        s.on_changed(on_slider_change)

    def on_key(event):
        if event.key == " ":
            state["running"] = not state["running"]
        elif event.key.lower() == "r":
            sim.reset()

    fig.canvas.mpl_connect("key_press_event", on_key)

    def update(_frame):
        if state["running"]:
            sim.step()

        hist = list(sim.history)
        xs = list(range(sim.ticks_per_life - len(hist), sim.ticks_per_life))
        line.set_data(xs, hist)
        dot.set_offsets([[xs[-1], hist[-1]]])

        lo, hi = min(hist + [params["K"]]), max(hist + [params["K"]])
        pad = (hi - lo) * 0.15 or hi * 0.1 or 5
        ax.set_ylim(lo - pad, hi + pad)

        change = sim.S - sim.s0
        pct = change / sim.s0 * 100
        arrow = "+" if change >= 0 else ""
        title_text.set_text(f"SIM  ${sim.S:6.2f}   {arrow}{change:.2f} ({arrow}{pct:.2f}%)")
        title_text.set_color("#35D68C" if change >= 0 else "#FF5D5D")

        remaining_secs = sim.remaining_day() * 86400
        status = "EXPIRED" if sim.expired else ("RUNNING" if state["running"] else "PAUSED")
        info_text.set_text(f"t-to-expiry: {remaining_secs:6.2f}d   status: {status}")

        bs = black_scholes(sim.S, params["K"], sim.remaining_day(), params["r"], sim.sigma)
        call_text.set_text(
            f"CALL ${bs['call']:6.2f}  d={bs['call_delta']:+.3f}  "
            f"g={bs['gamma']:.4f}  th={bs['call_theta']:+.3f}  "
            f"v={bs['vega']:.3f}  rho={bs['call_rho']:+.3f}"
        )
        put_text.set_text(
            f"PUT  ${bs['put']:6.2f}  d={bs['put_delta']:+.3f}  "
            f"g={bs['gamma']:.4f}  th={bs['put_theta']:+.3f}  "
            f"v={bs['vega']:.3f}  rho={bs['put_rho']:+.3f}"
        )

        return line, dot, strike_line, title_text, info_text, call_text, put_text

    anim = FuncAnimation(fig, update, interval=100, blit=False, cache_frame_data=False)
    plt.show()


if __name__ == "__main__":
    main()
