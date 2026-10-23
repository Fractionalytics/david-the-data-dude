// Every number drawn in the Reel, copied from data/processed/ (rebuild with scripts/build_series.py).
// Census CPS Table A-1 throughout.

// Cards 1-2, 9-10: voters 65+ per voter 18-24, midterms (population x self-reported turnout, all adults).
// data/processed/senior_to_young_ratio.csv. 2022: 37,093k / 7,371k = 5.03.
// Three decimals so the drawn labels round correctly (2014 is 5.555 -> "5.6", as spoken).
export const RATIO: [number, number][] = [
	[1974, 1.76], [1978, 1.977], [1982, 2.145], [1986, 2.916], [1990, 3.556], [1994, 3.771], [1998, 4.528],
	[2002, 4.39], [2006, 3.921], [2010, 4.049], [2014, 5.555], [2018, 3.796], [2022, 5.032],
];

// Card 4: adults by age group, millions, election years 1972-2024 (turnout_by_age.csv, population_k).
// Starts 1972: before the 26th Amendment CPS's 18-24 group mostly held 21-24-year-olds.
export const ADULTS = {
	young: [24.6, 25.7, 27.0, 27.7, 28.1, 28.8, 28.0, 26.4, 25.6, 24.8, 24.4, 25.2, 24.6, 25.5, 26.7, 27.4, 27.8, 27.8, 28.3, 28.9, 29.9, 29.7, 29.3, 29.0, 28.7, 28.8, 30.0],
	old: [20.1, 21.0, 22.0, 23.0, 24.1, 25.6, 26.7, 27.7, 28.8, 29.9, 30.8, 31.1, 31.9, 32.3, 32.8, 33.9, 34.7, 35.8, 37.5, 39.0, 42.5, 45.6, 48.7, 51.9, 55.3, 57.4, 60.4],
};
export const ADULT_YEARS = ADULTS.young.map((_, i) => 1972 + 2 * i);

// Cards 6-8: % of citizens who say they voted (turnout_by_age.csv, cps_citizen_turnout).
// Spoken: "just 8 percentage points" (7.7) and "dropped 24 points" (23.8); card 8: 17.1 -> 32.4 = +89%.
export const DROP = {
	old: {from: 74.5, to: 66.8},
	young: {from: 51.4, to: 27.6},
};
export const YOUNG_MIDTERM = {from: 17.1, to: 32.4};
