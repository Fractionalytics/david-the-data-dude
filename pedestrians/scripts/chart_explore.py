"""Exploratory charts for the sedans-to-SUVs project (2026-11-05).

    python scripts/chart_explore.py
      -> charts/top25_2025_by_type.png        best-selling vehicles of 2025, colored by type
      -> charts/phones_vs_pedestrians.png     phone ownership and pedestrian deaths, stacked panels

Reads data/raw/sales/top25_2025.csv, data/raw/pew/phone_ownership.csv and
data/raw/iihs/pedestrian_deaths.csv.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INK, MUTED, RULE, SURFACE = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
# default categorical slots 1-4 (validated, dataviz skill)
TYPES = {"Car": "#2a78d6", "SUV/crossover": "#eb6834", "Pickup": "#1baf7a", "Van": "#eda100"}


def style(ax) -> None:
    ax.set_facecolor(SURFACE)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(RULE)
    ax.tick_params(colors=MUTED)
    ax.set_axisbelow(True)


def top25() -> None:
    d = pd.read_csv(ROOT / "data" / "raw" / "sales" / "top25_2025.csv").sort_values("units_2025")
    fig, ax = plt.subplots(figsize=(8, 9), facecolor=SURFACE)
    style(ax)
    ax.barh(d.model, d.units_2025 / 1000, color=d.type.map(TYPES), height=0.72, edgecolor=SURFACE, linewidth=1.5)
    for y, (v, m) in enumerate(zip(d.units_2025, d.model)):
        ax.text(v / 1000 + 8, y, f"{v / 1000:,.0f}k", va="center", fontsize=8, color=MUTED)
    ax.grid(axis="x", color=RULE)
    ax.tick_params(axis="y", length=0, labelcolor=INK)
    ax.set_xlabel("US sales, 2025 (thousands)", color=MUTED)
    ax.set_title("America's 25 best-selling vehicles, 2025", loc="left", color=INK, fontsize=11)
    shares = d.groupby("type").units_2025.sum() / d.units_2025.sum()
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in TYPES.values()]
    ax.legend(handles, [f"{t} ({(d.type == t).sum()} models, {shares.get(t, 0):.0%} of top-25 sales)" for t in TYPES],
              loc="lower right", frameon=False, fontsize=8, labelcolor=INK)
    fig.text(0.01, 0.005, "Source: Car and Driver via CarPro. Tesla Model Y not listed (Tesla doesn't report by model; "
             "est. ~318k would rank 7th). Types are ours.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(ROOT / "charts" / "top25_2025_by_type.png", dpi=150, facecolor=SURFACE)
    print(shares.round(3).to_string())


def phones() -> None:
    p = pd.read_csv(ROOT / "data" / "raw" / "pew" / "phone_ownership.csv", parse_dates=["survey_date"])
    p["year"] = p.survey_date.dt.year + (p.survey_date.dt.dayofyear - 1) / 365
    ped = pd.read_csv(ROOT / "data" / "raw" / "iihs" / "pedestrian_deaths.csv")
    ped = ped[ped.year >= 2000]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True, facecolor=SURFACE,
                                 gridspec_kw={"hspace": 0.25})
    for ax in (a1, a2):
        style(ax)
        ax.grid(axis="y", color=RULE)
        ax.axvline(2007.5, color=MUTED, linestyle=(0, (3, 3)), linewidth=1)
    for dev, mk in (("cellphone", "o"), ("smartphone", "o")):
        s = p[p.device == dev]
        a1.plot(s.year, s.share_pct, marker=mk, markersize=4, linewidth=2,
                color="#8a8985" if dev == "cellphone" else "#2a78d6", label=f"Own a {dev}")
    a1.set_ylim(0, 100)
    a1.set_title("Share of US adults who own a phone (%)", loc="left", color=INK, fontsize=11)
    a1.legend(frameon=False, fontsize=8, labelcolor=INK, loc="lower right")
    a1.text(2007.6, 5, "iPhone launches, June 2007", color=MUTED, fontsize=8)
    a2.plot(ped.year, ped.pedestrian_deaths, color="#eb6834", linewidth=2, marker="o", markersize=3)
    a2.set_ylim(0, 8000)
    a2.set_title("US pedestrian deaths per year", loc="left", color=INK, fontsize=11)
    fig.text(0.01, 0.005, "Sources: Pew Research Center (smartphones asked from 2011; cellphones before); "
             "IIHS from NHTSA FARS.", fontsize=7, color=MUTED)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.08)
    fig.savefig(ROOT / "charts" / "phones_vs_pedestrians.png", dpi=150, facecolor=SURFACE)


def fars() -> None:
    """Pedestrian deaths by light and road (stacked), sidewalk share, and striking vehicle, from FARS."""
    f = ROOT / "data" / "final"
    da = pd.read_csv(f / "fars_ped_dark_arterial.csv").set_index("year")
    lt = pd.read_csv(f / "fars_ped_by_light.csv").set_index("year")
    sw = pd.read_csv(f / "fars_ped_by_sidewalk.csv").set_index("year")
    vh = pd.read_csv(f / "fars_ped_by_vehicle.csv").set_index("year")
    parts = pd.DataFrame({"Dark, arterial road": da.dark_arterial,
                          "Dark, other roads": da.dark - da.dark_arterial,
                          "Daylight, dawn or dusk": lt.total - lt.dark})
    colors = ["#eb6834", "#f4a582", "#b5b4ae"]

    fig, axes = plt.subplots(3, 1, figsize=(9, 11), facecolor=SURFACE, sharex=True, gridspec_kw={"hspace": 0.3})
    a1, a2, a3 = axes
    for ax in axes:
        style(ax)
        ax.grid(axis="y", color=RULE)
    bottom = 0
    for (name, s), c in zip(parts.items(), colors):
        a1.bar(s.index, s, bottom=bottom, color=c, width=0.75, edgecolor=SURFACE, linewidth=1, label=name)
        bottom = bottom + s
    a1.set_title("US pedestrian deaths by light and road type", loc="left", color=INK, fontsize=11)
    a1.legend(frameon=False, fontsize=8, labelcolor=INK, loc="upper left")
    for y in (2000, 2009, 2024):
        a1.text(y, parts.loc[y].sum() + 80, f"{da.dark_arterial[y]:,}", ha="center", fontsize=7, color="#eb6834")

    a2.plot(vh.index, vh.light_truck_share_of_known * 100, color="#1baf7a", linewidth=2, marker="o", markersize=3,
            label="Light truck (SUV, pickup, van)")
    a2.plot(vh.index, vh.car_share_of_known * 100, color="#2a78d6", linewidth=2, marker="o", markersize=3,
            label="Passenger car")
    a2.set_ylim(0, 70)
    a2.set_title("Vehicle that struck the pedestrian, % of deaths with a known vehicle type", loc="left",
                 color=INK, fontsize=11)
    a2.legend(frameon=False, fontsize=8, labelcolor=INK, loc="lower left")

    a3.plot(sw.index, sw.none_noted_share * 100, color="#8a8985", linewidth=2, marker="o", markersize=3)
    a3.set_ylim(0, 100)
    a3.set_title("No sidewalk noted at the crash site, % of pedestrian deaths (field starts 2014)", loc="left",
                 color=INK, fontsize=11)
    fig.text(0.01, 0.005, "Source: NHTSA FARS 2000-2024 (2024 not yet final). Dark includes lighted and unlit. "
             "Arterial = principal + minor arterials, not freeways;\nroad codes changed in 2015. "
             "'No sidewalk noted' includes reports that didn't record one.", fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.96, bottom=0.05)
    fig.savefig(ROOT / "charts" / "fars_light_road_vehicle_sidewalk.png", dpi=150, facecolor=SURFACE)


def us_eu() -> None:
    """Pedestrian deaths per 100,000: US against the EU and its four biggest countries plus the UK."""
    d = pd.read_csv(ROOT / "data" / "final" / "eu_pedestrian_rates.csv")
    p = d.pivot_table(index="year", columns="geo", values="rate_per_100k")
    # matched definitions: EU = 18 members reporting every year; US = pedestrians + personal conveyances
    m = pd.read_csv(ROOT / "data" / "final" / "us_eu_decompose.csv")
    m = m[m.group == "pedestrian"].pivot_table(index="year", columns="geo", values="rate_per_100k")
    p["EU27_2020"], p["US"] = m["EU fixed"], m["US"]
    names = {"EU27_2020": "EU (18)", "DE": "Germany", "FR": "France", "ES": "Spain", "IT": "Italy", "UK": "UK"}
    fig, ax = plt.subplots(figsize=(9, 5.5), facecolor=SURFACE)
    style(ax)
    ax.grid(axis="y", color=RULE)
    ends = p[list(names)].iloc[-1].sort_values()
    label_y, last = {}, -1.0
    for g, v in ends.items():  # spread end labels at least 0.06 apart
        last = max(v, last + 0.06)
        label_y[g] = last
    for g, n in names.items():
        lw, c = (2.5, "#2a78d6") if g == "EU27_2020" else (1.2, "#b5b4ae")
        ax.plot(p.index, p[g], color=c, linewidth=lw)
        ax.text(p.index[-1] + 0.3, label_y[g], n, va="center", fontsize=8, color=c if g == "EU27_2020" else MUTED)
    ax.plot(p.index, p["US"], color="#eb6834", linewidth=2.5)
    ax.text(p.index[-1] + 0.3, p["US"].iloc[-1], "US", va="center", fontsize=9, color="#eb6834", fontweight="bold")
    ax.set_xlim(1999.5, 2026.5)
    ax.set_ylim(0, 2.5)
    ax.set_title("Pedestrian deaths per 100,000 people", loc="left", color=INK, fontsize=11)
    fig.text(0.01, 0.005, "Sources: Eurostat (EU = the 18 members that reported every year 2000-2024; UK 2019-24 from DfT, "
             "Great Britain only); US: NHTSA FARS pedestrians plus people on personal\nconveyances (the international "
             "definition, as in the CDC's comparison), over Census population.", fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.07, right=0.93, top=0.93, bottom=0.1)
    fig.savefig(ROOT / "charts" / "us_eu_pedestrian_rates.png", dpi=150, facecolor=SURFACE)


def vehicle_mix() -> None:
    """New vehicles per 1,000 people by type: US cars vs. light trucks, EU non-SUV cars vs. SUVs."""
    d = pd.read_csv(ROOT / "data" / "final" / "eu_new_cars_suv.csv")
    eu = d[d.geo == "EU27"].set_index("year")
    pop = pd.read_csv(ROOT / "data" / "raw" / "fred" / "POPTHM.csv", parse_dates=[0]).set_index("observation_date").iloc[:, 0]
    pop = pop.groupby(pop.index.year).mean()

    def fred(s):
        x = pd.read_csv(ROOT / "data" / "raw" / "fred" / f"{s}.csv", parse_dates=[0]).set_index("observation_date").iloc[:, 0]
        return x.groupby(x.index.year).mean()  # seasonally adjusted annual rate, millions

    yrs = range(2001, 2025)
    us = pd.DataFrame({"cars": fred("LAUTOSA"), "trucks": fred("LTRUCKSA")}).loc[yrs].mul(1e6).div(pop.loc[yrs] * 1e3, axis=0) * 1000
    eu_suv = eu.suv_count / eu.total_new_cars * eu.per_1000
    eu_other = eu.per_1000 - eu_suv

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 5), sharey=True, facecolor=SURFACE, gridspec_kw={"wspace": 0.08})
    for ax in (a1, a2):
        style(ax)
        ax.grid(axis="y", color=RULE)
    a1.plot(us.index, us.cars, color="#2a78d6", linewidth=2.5, label="Cars (sedans, coupes, hatchbacks, wagons)")
    a1.plot(us.index, us.trucks, color="#1baf7a", linewidth=2.5, label="Light trucks (SUVs, pickups, vans)")
    a1.set_title("US: new vehicles per 1,000 people", loc="left", color=INK, fontsize=11)
    a1.legend(frameon=False, fontsize=8, labelcolor=INK, loc="upper left")
    a2.plot(eu_other.index, eu_other, color="#2a78d6", linewidth=2.5, label="Cars other than SUVs")
    a2.plot(eu_suv.index, eu_suv, color="#eb6834", linewidth=2.5, label="SUVs")
    a2.set_title("EU-27: new passenger cars per 1,000 people", loc="left", color=INK, fontsize=11)
    a2.legend(frameon=False, fontsize=8, labelcolor=INK, loc="upper right")
    fig.text(0.01, 0.005, "Sources: US: BEA light-vehicle sales via FRED, Census population. EU: Eurostat (2013+) and ICCT "
             "(2001-12) registrations; SUV share from ICCT's chart.\nUS 'light trucks' include pickups and vans; "
             "EU registers most pickups as vans, so not shown.", fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.92, bottom=0.12)
    fig.savefig(ROOT / "charts" / "vehicle_mix_us_eu_per_1000.png", dpi=150, facecolor=SURFACE)
    print(pd.DataFrame({"us_cars": us.cars, "us_trucks": us.trucks, "eu_other": eu_other, "eu_suv": eu_suv}).loc[[2001, 2007, 2013, 2019, 2024]].round(1))


def decompose() -> None:
    """Pedestrian rates for US, EU West and EU East; then pedestrians vs. other road users, indexed to 2000."""
    d = pd.read_csv(ROOT / "data" / "final" / "us_eu_decompose.csv")
    r = d.pivot_table(index="year", columns=["geo", "group"], values="rate_per_100k")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5), facecolor=SURFACE, gridspec_kw={"wspace": 0.18})
    for ax in (a1, a2):
        style(ax)
        ax.grid(axis="y", color=RULE)
    for geo, c, lab in (("US", "#eb6834", "US"), ("EU West", "#2a78d6", "EU West (14 pre-2004 members)"),
                        ("EU East", "#8a8985", "EU East (CZ, PL, RO, SI)")):
        a1.plot(r.index, r[(geo, "pedestrian")], color=c, linewidth=2.5, label=lab)
    a1.set_ylim(0, 5.5)
    a1.set_title("Pedestrian deaths per 100,000 people", loc="left", color=INK, fontsize=11)
    a1.legend(frameon=False, fontsize=8, labelcolor=INK, loc="upper right")
    for geo, c in (("US", "#eb6834"), ("EU fixed", "#2a78d6")):
        for grp, ls in (("pedestrian", "-"), ("other road users", (0, (4, 3)))):
            s = r[(geo, grp)]
            name = "US" if geo == "US" else "EU (18 members)"
            a2.plot(s.index, s / s.iloc[0] * 100, color=c, linestyle=ls, linewidth=2.5, label=f"{name}: {grp}")
    a2.axhline(100, color=MUTED, linewidth=0.8)
    a2.set_title("Road deaths per person, indexed to 2000 = 100", loc="left", color=INK, fontsize=11)
    a2.legend(frameon=False, fontsize=8, labelcolor=INK, loc="lower left")
    fig.text(0.01, 0.005, "Sources: Eurostat (18 EU members that reported every year 2000-2024); US: NHTSA FARS, pedestrians "
             "plus people on personal conveyances (the international definition), all road deaths from IIHS.",
             fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.05, right=0.98, top=0.92, bottom=0.1)
    fig.savefig(ROOT / "charts" / "us_eu_decompose.png", dpi=150, facecolor=SURFACE)


def increase() -> None:
    """Where the 2009 -> 2022 rise in US pedestrian deaths happened: change in deaths by category, six panels."""
    d = pd.read_csv(ROOT / "data" / "final" / "fars_decompose_share_of_increase.csv")
    panels = [("hour", "Time of day"), ("urban_rural", "Urban or rural"), ("age", "Age of the pedestrian"),
              ("region", "Region"), ("hit_run", "Hit-and-run"), ("sex", "Sex")]
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), facecolor=SURFACE, gridspec_kw={"hspace": 0.45, "wspace": 0.55})
    for ax, (dim, title) in zip(axes.flat, panels):
        style(ax)
        s = d[(d.dimension == dim) & (d.category != "unknown")].set_index("category").change_to_2022.sort_values()
        short = {"overnight_midnight_6am": "midnight-6am", "evening_6_9pm": "6-9pm",
                 "late_evening_9pm_midnight": "9pm-midnight", "daytime_6am_6pm": "6am-6pm"}
        ax.barh([short.get(c, c.replace("_", " ")) for c in s.index], s, color=["#eb6834" if v > 0 else "#2a78d6" for v in s], height=0.65)
        for y, v in enumerate(s):
            ax.text(v + (40 if v >= 0 else -40), y, f"{v:+,.0f}", va="center", ha="left" if v >= 0 else "right",
                    fontsize=7.5, color=MUTED)
        ax.axvline(0, color=MUTED, linewidth=0.8)
        ax.set_xlim(min(-300, s.min() - 300), 3900)
        ax.grid(axis="x", color=RULE)
        ax.tick_params(axis="y", length=0, labelcolor=INK, labelsize=8)
        ax.set_title(title, loc="left", color=INK, fontsize=10)
    fig.suptitle("Change in US pedestrian deaths, 2009 to 2022 (total +3,484)", x=0.01, ha="left", color=INK, fontsize=12)
    fig.text(0.01, 0.005, "Source: NHTSA FARS (scripts/fars_decompose.py). Dark hours: 6pm-6am. Urban/rural field changed "
             "in 2015. Region = Census region of the crash.", fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.9, bottom=0.06)
    fig.savefig(ROOT / "charts" / "where_the_increase_is.png", dpi=150, facecolor=SURFACE)


def drugs() -> None:
    """Pedestrians killed (top) and the share of those tested who were positive for a stimulant or opioid (bottom)."""
    d = pd.read_csv(ROOT / "data" / "final" / "test_ped_drugs.csv")
    d = d[(d.definition == "primary") & d.year.astype(str).str.isdigit()].astype({"year": int}).set_index("year")
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True, facecolor=SURFACE, gridspec_kw={"hspace": 0.25})
    for ax in (a1, a2):
        style(ax)
        ax.grid(axis="y", color=RULE)
    a1.plot(d.index, d.killed, color="#eb6834", linewidth=2.5, marker="o", markersize=3)
    a1.set_ylim(0, 8000)
    a1.set_title("US pedestrians killed per year", loc="left", color=INK, fontsize=11)
    a2.plot(d.index, d.share_stimulant * 100, color="#2a78d6", linewidth=2.5, marker="o", markersize=3,
            label="Stimulant (methamphetamine, amphetamine, cocaine)")
    a2.plot(d.index, d.share_opioid * 100, color="#1baf7a", linewidth=2.5, marker="o", markersize=3,
            label="Opioid (including fentanyl)")
    a2.set_ylim(0, 40)
    a2.set_title("Of pedestrians killed and tested for drugs, % positive", loc="left", color=INK, fontsize=11)
    a2.legend(frameon=False, fontsize=8, labelcolor=INK, loc="upper left")
    fig.text(0.01, 0.005, "Source: NHTSA FARS (scripts/test_ped_drugs.py). About 50-62% of pedestrians killed were tested "
             "after 2008 (40-53% before). A positive test isn't impairment or cause.", fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.08)
    fig.savefig(ROOT / "charts" / "pedestrian_drug_tests.png", dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    top25()
    phones()
    fars()
    us_eu()
    vehicle_mix()
    decompose()
    increase()
    drugs()
