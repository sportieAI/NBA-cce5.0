import sys

print("\n🔥 FINAL VERDICT: GOLDEN STATE WARRIORS vs PHOENIX SUNS")
print("=======================================================")

# --- THE MATH (CCE V5.0 Logic) ---
# GSW (Home) vs PHX (Away)
# GSW NetRtg: +5.0 | PHX NetRtg: +6.2
# Difference: -1.2 (Suns have raw statistical edge)

net_diff = -1.2
delta_w_fund = net_diff * 0.5  # Fundamental Anchor = -0.6

# --- THE HUMAN ELEMENT ---
# Steve Kerr Adjustment (Coaching IQ) + Chase Center (Home)
human_signal = 1.5 

# --- THE CALCULATION ---
# -0.6 (Stats) + 1.5 (Human) = +0.9 (Final Edge)
final_margin = delta_w_fund + human_signal

print(f"�� Statistical Anchor: {delta_w_fund:.2f} (Suns Edge)")
print(f"🧠 Human Signal:      +{human_signal:.2f} (Warrior Resilience)")
print("-------------------------------------------------------")

if final_margin > 0:
    print(f"🏆 PREDICTION: GSW WINS by {abs(final_margin):.1f} points")
    print("✅ SIGNAL: TRUST THE DYNASTY")
else:
    print(f"🏆 PREDICTION: PHX WINS by {abs(final_margin):.1f} points")

print("=======================================================")
