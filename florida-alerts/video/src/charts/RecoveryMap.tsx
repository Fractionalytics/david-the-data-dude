// Card 8 (2:00:20–2:16:21): where state Silver Alert subjects were found, 2011–2020.
//   Opens on Florida (2,035 found there). Pans north to take in Georgia, landing on David's
//   "Georgia" cue at 2:07:16 (82 found there). Then zooms out fast to the lower 48, landing on the
//   Washington beat at 2:11:21, with every state where someone was found filled in, and a dot on
//   Puyallup, WA. Holds to the end of the card.
// The map is re-projected every frame (d3-geo), so borders stay crisp at every zoom level.
import React, {useMemo} from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {geoAlbers, geoPath, type GeoProjection} from 'd3-geo';
import {feature} from 'topojson-client';
import type {Feature, FeatureCollection, Geometry} from 'geojson';
import us from 'us-atlas/states-10m.json';
import data from '../data/silver.json';
import {INK, Page, Scrawl, ScopeNote, ZONES, clamp, cue} from '../sharpie';

const GEORGIA = cue(8, 2, 7, 16); // Georgia filled and labeled by here
const WASHINGTON = cue(8, 2, 11, 21); // whole country in view, Washington labeled by here
const PAN = 45; // frames for the Florida -> Georgia pan
const ZOOM_OUT = 24; // frames for the fast zoom out to the whole country

const FOUND_HERE = '#f07f13'; // orange: a state where someone was found (not a "because of the alert" claim)
const FLORIDA_FILL = '#cfe0f5';

const NAME_TO_CODE: Record<string, string> = {
	Alabama: 'AL', Arizona: 'AZ', Arkansas: 'AR', California: 'CA', Colorado: 'CO', Connecticut: 'CT', Delaware: 'DE',
	'District of Columbia': 'DC', Florida: 'FL', Georgia: 'GA', Idaho: 'ID', Illinois: 'IL', Indiana: 'IN', Iowa: 'IA',
	Kansas: 'KS', Kentucky: 'KY', Louisiana: 'LA', Maine: 'ME', Maryland: 'MD', Massachusetts: 'MA', Michigan: 'MI',
	Minnesota: 'MN', Mississippi: 'MS', Missouri: 'MO', Montana: 'MT', Nebraska: 'NE', Nevada: 'NV', 'New Hampshire': 'NH',
	'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', Ohio: 'OH',
	Oklahoma: 'OK', Oregon: 'OR', Pennsylvania: 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
	Tennessee: 'TN', Texas: 'TX', Utah: 'UT', Vermont: 'VT', Virginia: 'VA', Washington: 'WA', 'West Virginia': 'WV',
	Wisconsin: 'WI', Wyoming: 'WY',
};

type State = Feature<Geometry, {name: string}>;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const ALL = (feature(us as any, (us as any).objects.states) as unknown as FeatureCollection<Geometry, {name: string}>).features;
const LOWER48 = ALL.filter((f) => NAME_TO_CODE[f.properties.name]) as State[];
const COLLECTION: FeatureCollection = {type: 'FeatureCollection', features: LOWER48};
const byCode = (code: string) => LOWER48.find((f) => NAME_TO_CODE[f.properties.name] === code)!;
const COUNTS = data.states as Record<string, number>;
const PUYALLUP: [number, number] = [-122.29, 47.19];

// The map fills this box; labels and the scope note sit inside the chart zone around it.
const BOX = {left: ZONES.chart.left + 10, right: ZONES.chart.right - 10, top: ZONES.chart.top + 110, bottom: ZONES.chart.bottom - 100};
const BOX_CENTER: [number, number] = [(BOX.left + BOX.right) / 2, (BOX.top + BOX.bottom) / 2];
const BASE = geoAlbers().fitExtent(
	[
		[BOX.left, BOX.top],
		[BOX.right, BOX.bottom],
	],
	COLLECTION,
);
const BASE_SCALE = BASE.scale();
const BASE_T = BASE.translate();
const basePath = geoPath(BASE);

type View = {k: number; cx: number; cy: number};
// The zoom that fits a set of states into BOX, with some breathing room.
const viewOf = (features: Feature[], pad = 1.25): View => {
	const [[x0, y0], [x1, y1]] = basePath.bounds({type: 'FeatureCollection', features} as FeatureCollection);
	const k = Math.min((BOX.right - BOX.left) / ((x1 - x0) * pad), (BOX.bottom - BOX.top) / ((y1 - y0) * pad));
	return {k, cx: (x0 + x1) / 2, cy: (y0 + y1) / 2};
};
const V_FLORIDA = viewOf([byCode('FL')]);
const V_GEORGIA = viewOf([byCode('FL'), byCode('GA')], 1.15);
const V_ALL: View = {k: 1, cx: BOX_CENTER[0], cy: BOX_CENTER[1]};

const blend = (a: View, b: View, t: number): View => ({
	k: Math.exp(Math.log(a.k) + (Math.log(b.k) - Math.log(a.k)) * t),
	cx: a.cx + (b.cx - a.cx) * t,
	cy: a.cy + (b.cy - a.cy) * t,
});

const viewAt = (frame: number): View => {
	const ease = {...clamp, easing: Easing.inOut(Easing.cubic)};
	if (frame < GEORGIA) return blend(V_FLORIDA, V_GEORGIA, interpolate(frame, [GEORGIA - PAN, GEORGIA], [0, 1], ease));
	return blend(V_GEORGIA, V_ALL, interpolate(frame, [WASHINGTON - ZOOM_OUT, WASHINGTON], [0, 1], ease));
};

const projectionFor = (v: View): GeoProjection =>
	geoAlbers()
		.scale(BASE_SCALE * v.k)
		.translate([BASE_T[0] * v.k - v.k * v.cx + BOX_CENTER[0], BASE_T[1] * v.k - v.k * v.cy + BOX_CENTER[1]]);

// When each state fills in: Florida from the start, Georgia on its cue, the rest as the map zooms out.
const fillIn = (code: string, frame: number) => {
	if (code === 'FL') return interpolate(frame, [0, 15], [0, 1], clamp);
	if (code === 'GA') return interpolate(frame, [GEORGIA - 15, GEORGIA], [0, 1], clamp);
	return interpolate(frame, [WASHINGTON - ZOOM_OUT / 2, WASHINGTON], [0, 1], clamp);
};

export const RecoveryMap: React.FC = () => {
	const frame = useCurrentFrame();
	const projection = useMemo(() => projectionFor(viewAt(frame)), [frame]);
	const path = geoPath(projection);
	const label = (code: string, at: number) => {
		const [x, y] = path.centroid(byCode(code));
		return {x, y, opacity: interpolate(frame, [at - 8, at], [0, 1], clamp)};
	};
	// Labels shrink as the map zooms out, and Florida's moves offshore so it doesn't cover Georgia.
	const out = interpolate(frame, [WASHINGTON - ZOOM_OUT, WASHINGTON], [0, 1], clamp);
	const labelSize = 56 - 22 * out;
	const fl = label('FL', 15);
	const flEast = path.bounds(byCode('FL'))[1][0] + 70;
	fl.x = fl.x + 20 + (flEast - fl.x - 20) * out;
	const ga = label('GA', GEORGIA);
	const [px, py] = projection(PUYALLUP) ?? [0, 0];
	const wa = interpolate(frame, [WASHINGTON - 8, WASHINGTON], [0, 1], clamp);

	return (
		<Page>
			<clipPath id="map-zone">
				<rect x={ZONES.chart.left} y={ZONES.chart.top} width={ZONES.chart.right - ZONES.chart.left} height={ZONES.chart.bottom - ZONES.chart.top} />
			</clipPath>
			<g clipPath="url(#map-zone)">
				<g filter="url(#marker-edge)">
					{LOWER48.map((f) => {
						const code = NAME_TO_CODE[f.properties.name];
						const n = COUNTS[code];
						const t = n ? fillIn(code, frame) : 0;
						const fill = code === 'FL' ? FLORIDA_FILL : FOUND_HERE;
						return (
							<g key={code}>
								<path d={path(f) ?? ''} fill="white" stroke={INK.black} strokeWidth={3} strokeLinejoin="round" />
								{t > 0 && <path d={path(f) ?? ''} fill={fill} fillOpacity={t} stroke={INK.black} strokeWidth={3} strokeLinejoin="round" />}
							</g>
						);
					})}
				</g>
				<Scrawl x={fl.x} y={fl.y + 20} size={labelSize} opacity={fl.opacity} seed="fl">
					{COUNTS.FL.toLocaleString('en-US')}
				</Scrawl>
				<Scrawl x={ga.x} y={ga.y} size={labelSize} opacity={ga.opacity} seed="ga">
					{COUNTS.GA}
				</Scrawl>
				<g opacity={wa}>
					<circle cx={px} cy={py} r={11} fill={INK.red} stroke={INK.black} strokeWidth={3} />
					<Scrawl x={px + 16} y={py - 50} size={38} anchor="start" seed="wa">
						Puyallup, WA
					</Scrawl>
				</g>
			</g>
			{/* Legend, once the whole country is in view. Series labels only; any title is David's. */}
			<g opacity={wa}>
				<rect x={ZONES.chart.left + 10} y={ZONES.chart.top + 25} width={38} height={38} fill={FOUND_HERE} stroke={INK.black} strokeWidth={3} />
				<Scrawl x={ZONES.chart.left + 64} y={ZONES.chart.top + 44} size={36} anchor="start" seed="lg">
					found here
				</Scrawl>
			</g>
			<ScopeNote opacity={interpolate(frame, [10, 25], [0, 1], clamp)}>State Silver Alerts, 2011–2020 · FDLE</ScopeNote>
		</Page>
	);
};
