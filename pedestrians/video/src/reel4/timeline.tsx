// What's on screen at global frame g of Reel 4. Card clips render their slice of this, so each clip starts
// from the previous card's end state. Line moves follow the Sheet's Video column (DDD17, Script v2); note
// text is the Sheet's On-Screen Text, word for word. Kickers, labels and source lines are ours.
// Cues inside a card are set a few frames after the card starts (no word-level timecodes).
import React from 'react';
import {AbsoluteFill, Easing} from 'remotion';
import {Legend, Marker, Slopegraph, Waves} from './charts';
import {S} from './cues';
import {clamp, LineKey, LINES, Note, Panel, prog, Stamp} from './kit';

type Move = [from: number, to: number, toYear: number]; // frames, and the year the line reaches
const lin = Easing.linear;
const io = Easing.inOut(Easing.quad);

// Card 1 draws all five lines one after another, 18 frames each, done by frame 90 (David: the first three
// seconds). Everything resets at card 4.
const HOOK: Record<LineKey, Move[]> = {
	w1: [[S(1), S(1) + 18, 2025]],
	w2: [[S(1) + 18, S(1) + 36, 2025]],
	w3: [[S(1) + 36, S(1) + 54, 2025]],
	w4: [[S(1) + 54, S(1) + 72, 2025]],
	stim: [[S(1) + 72, S(1) + 90, 2025]],
};
// From card 7 the lines rebuild, one cue at a time.
const BUILD: Record<LineKey, Move[]> = {
	w1: [[S(7) + 10, S(9), 2007], [S(10) + 6, S(10) + 110, 2025]], // cards 7-9 to 2007; card 10 to 2025
	w2: [[S(13) + 8, S(13) + 70, 2010], [S(14) + 10, S(14) + 40, 2011], [S(17) + 6, S(17) + 60, 2013], [S(18) + 6, S(18) + 90, 2017], [S(23) + 6, S(23) + 110, 2021], [S(30) + 10, S(30) + 120, 2025]],
	w3: [[S(19) + 6, S(19) + 80, 2013], [S(20) + 6, S(20) + 50, 2015], [S(23) + 6, S(23) + 110, 2021], [S(30) + 10, S(30) + 120, 2025]],
	w4: [[S(26) + 6, S(26) + 80, 2015], [S(27) + 6, S(27) + 130, 2023], [S(30) + 10, S(30) + 120, 2025]],
	stim: [[S(24) + 6, S(24) + 120, 2016], [S(27) + 6, S(27) + 130, 2023], [S(30) + 10, S(30) + 120, 2025]],
};

const reachAt = (moves: Move[], g: number) => {
	let yr = 2000;
	let moving = false;
	for (const [a, b, to] of moves) {
		if (g < a) break;
		yr += (to - yr) * prog(g, a, b, lin);
		if (g < b) moving = true;
	}
	return {yr, moving};
};

const fade = (g: number, inAt: number, outAt = Infinity, frames = 8) => Math.min(prog(g, inAt, inAt + frames, io), 1 - prog(g, outAt - frames, outAt, io));

// Note positions: the top-right box is clear until wave 3 climbs (card 23 on); the lower-left box under the
// key is clear the whole time (every line stays under ~12,000 before 2015).
const RIGHT = {x: 580, y: 312, w: 370};
const LEFT = {x: 190, y: 470, w: 430};

export const Graphic: React.FC<{g: number}> = ({g}) => {
	// Cards 4-6: the OxyContin slopegraph, no wave lines.
	const waveP = g < S(4) ? 1 : g < S(7) ? 1 - prog(g, S(4), S(4) + 8, io) : prog(g, S(7), S(7) + 8, io);
	const slopeP = g >= S(4) && g < S(7) + 8 ? Math.min(prog(g, S(4) + 4, S(4) + 12, io), 1 - prog(g, S(7) - 2, S(7) + 6, io)) : 0;
	const moves = g < S(4) ? HOOK : BUILD;
	const reach = {} as Record<LineKey, number>;
	const drawing = {} as Record<LineKey, boolean>;
	const show = {} as Record<LineKey, number>;
	for (const l of LINES) {
		const r = g >= S(4) && g < S(7) ? {yr: 2000, moving: false} : reachAt(moves[l.key], g);
		reach[l.key] = r.yr;
		drawing[l.key] = r.moving;
		show[l.key] = clamp((r.yr - 2000) * 2);
	}

	const markers: Marker[] = [
		// Card 10: Purdue stopped promoting opioids to doctors in Feb 2018 (shown as the line passes 2018).
		{yr: 2018.1, label: '2018 · PROMOTION STOPS', labelY: 600, anchor: 'end', p: fade(g, S(10) + 70, S(12))},
		{yr: 2010, label: '2010 · NEW OXYCONTIN', labelY: 600, anchor: 'end', p: fade(g, S(12) + 8, S(19))},
		{yr: 2011, label: '2011 · FLORIDA CRACKDOWN', labelY: 646, anchor: 'start', p: fade(g, S(14) + 6, S(19))},
		// Card 20: illicit fentanyl from China arrives (Ciccarone dates wave 3 from 2013).
		{yr: 2013, label: '2013 · CHINESE FENTANYL', labelY: 640, anchor: 'end', p: fade(g, S(20) + 6, S(24))},
		{yr: 2019, label: '2019 · CLASS BAN', labelY: 340, lineTop: 354, anchor: 'end', p: fade(g, S(32) + 10, S(37)), dots: ['w3', 'w4']},
		{yr: 2023.5, label: 'MID-2023', labelY: 795, anchor: 'end', p: fade(g, S(33) + 8, S(37)), dots: ['w3', 'w4'], lineTop: 200},
	];
	// Card 17: heroin deaths jump the year after the reformulation (2,991 in 2010 to 4,353 in 2011).
	const jumpP = fade(g, S(17) + 8, S(18));

	return (
		<AbsoluteFill>
			<Panel>
				<AbsoluteFill style={{opacity: waveP}}>
					<Waves reach={reach} drawing={drawing} axesP={1} markers={markers}>
						<Legend show={show} p={1} />
					</Waves>
					{jumpP > 0 && (
						<svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0, opacity: jumpP}}>
							<text x={530} y={880} fontFamily='Consolas, "Courier New", monospace' fontSize={30} fontWeight={700} fill={LINES[1].color}>+46% IN 2011</text>
						</svg>
					)}
				</AbsoluteFill>
				<AbsoluteFill style={{opacity: slopeP}}>
					<Slopegraph p={prog(g, S(4) + 14, S(4) + 54)} refP={prog(g, S(6) + 4, S(6) + 14, io)} />
				</AbsoluteFill>

				{/* Cards 2-3 */}
				<Note {...LEFT} p={fade(g, S(2) + 4, S(4))} lines={['Credit for 4 Waves concept: Daniel Ciccarone, MD, MPH, UC San Francisco']} source="Ciccarone, Int J Drug Policy 2019 and 2021" />
				{/* Card 9 */}
				<Note {...RIGHT} p={fade(g, S(9) + 6, S(10))} size={24} lines={['$600M paid by Purdue Frederick', '$34.5M paid by three executives', 'for felony misbranding "with the intent to defraud or mislead"']} source="US Attorney Brownlee, Senate testimony, 2007" />
				{/* Card 8: David's text; "mostly" added because 439 of the 608 citations (72%) used the letter as
				    evidence addiction was rare (Leung et al., NEJM 2017). */}
				<Note x={190} y={372} w={760} p={fade(g, S(8) + 6, S(9))} size={34} lines={['A short note about hospitalized patients was used to sell take-home pills.']} fine={'The "hospital letter" was a brief letter to the editor of the New England Journal of Medicine about patients in a hospital. It was not a scientific study. It said nothing about patients taking opioids for months at home. Nonetheless it was cited over 600 times by 2017, mostly as evidence addiction was rare.'} source="Porter & Jick, NEJM 1980 · Leung et al., NEJM 2017" />
				{/* Card 10 */}
				<Note {...RIGHT} p={fade(g, S(10) + 20, S(12))} size={24} lines={['Purdue stopped marketing OxyContin after years of falling sales and mounting lawsuits.']} source="PBS · Bloomberg, Feb 2018" />
				{/* Card 14 */}
				<Note {...RIGHT} p={fade(g, S(14) + 10, S(15))} size={23} lines={['In 2010, 90 of the top 100 oxycodone-buying doctors in the US were in Florida.', 'Florida’s oxycodone deaths fell 52% from 2010 to 2012.']} source="DEA 2013 · CDC MMWR 2014" />
				{/* Card 18: the book, as a typed reference */}
				<Note {...RIGHT} p={fade(g, S(18) + 6, S(19))} kicker="Further reading" lines={['Dreamland', 'Sam Quinones, 2015']} size={30} source="The true tale of America's opiate epidemic" />
				{/* Card 20: how the fentanyl came in */}
				<Note {...RIGHT} p={fade(g, S(20) + 10, S(21))} kicker="How it got in" size={26} lines={['China → Mexico → US', 'China → Canada → US', 'China → mail → US']} source="Ciccarone 2019 · DEA" />
				{/* Card 22 */}
				<Note {...RIGHT} p={fade(g, S(22) + 4, S(23))} size={26} lines={['According to the DEA']} />
				{/* Cards 33-34 */}
				<Note {...LEFT} p={fade(g, S(33) + 8, S(35))} size={23} lines={['A quiet Chinese crackdown under US pressure is suspected, but unproven.', 'China’s formal controls came afterward.']} source="Vangelov et al., Science 2026 · DEA NDTA 2025" />
				{/* Card 35 */}
				<Note {...LEFT} p={fade(g, S(35) + 6, S(36))} size={24} lines={['- Narcan moved to OTC', '- Testing kits legalized', '- Overdose prevention centers legalized in some places']} source="FDA 2023 · state laws" />
				{/* Card 37 */}
				<Stamp x={405} y={560} text="700K+" sub="deaths in the four waves, 2000–2025" p={prog(g, S(37) + 6, S(37) + 16, Easing.out(Easing.quad))} size={120} />
			</Panel>
		</AbsoluteFill>
	);
};
