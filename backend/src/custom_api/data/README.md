Real-time stock price generator using Geometric Brownian Motion (GBM),
with live Black-Scholes option pricing and Greeks.

GBM is the stochastic process the Black-Scholes model assumes for the
underlying asset:

    S(t + dt) = S(t) * exp((mu - 0.5 * sigma**2) * dt + sigma * sqrt(dt) * Z)

where Z ~ N(0, 1). Each frame of the animation advances the price by one
step and recomputes the Black-Scholes call/put price and Greeks from the
current simulated price and the remaining time to expiry.

Requirements:
    pip install numpy matplotlib

Run:
    python black_scholes_simulator.py

Controls:
    Sliders at the bottom adjust mu, sigma, r, K live.
    Space bar: pause / resume
    R key: reset the simulation