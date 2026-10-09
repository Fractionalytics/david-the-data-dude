// Carousel slide 9 (1080×1350): the Reel's cover plus a QR code that opens the Reel.
// Neither Instagram carousels nor LinkedIn PDFs make links on a slide clickable, so the QR code is the way
// through on both (and for desktop viewers). The QR is drawn as plain square modules, not in the Sharpie style,
// so phones can scan it. The only text is the URL, in a plain font because it's case-sensitive; any call to action is David's caption.
import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import QRCode from 'qrcode';
import {CAROUSEL} from '@kit/scorecard';
import {INK} from '../sharpie';

export const REEL_URL = 'https://www.instagram.com/reel/DePwOM8S0_S/';
const W = CAROUSEL.width;
const H = CAROUSEL.height;
const COVER_H = 860;
const COVER_W = (COVER_H * 1080) / 1920;
const QR_SIZE = 380;

export const ReelQr: React.FC = () => {
	const qr = QRCode.create(REEL_URL, {errorCorrectionLevel: 'M'});
	const n = qr.modules.size;
	const quiet = 4; // standard quiet zone, in modules
	const cell = QR_SIZE / (n + 2 * quiet);
	const rects: React.ReactNode[] = [];
	for (let r = 0; r < n; r++) {
		for (let c = 0; c < n; c++) {
			if (qr.modules.get(r, c)) {
				rects.push(<rect key={`${r}-${c}`} x={(c + quiet) * cell} y={(r + quiet) * cell} width={cell + 0.5} height={cell + 0.5} fill="#000" />);
			}
		}
	}
	const coverLeft = 90;
	const coverTop = (H - COVER_H) / 2 - 40;
	const qrLeft = W - 90 - QR_SIZE;
	const qrTop = coverTop + (COVER_H - QR_SIZE) / 2;
	return (
		<AbsoluteFill style={{backgroundColor: 'white'}}>
			<Img
				src={staticFile('cover.jpg')}
				style={{position: 'absolute', left: coverLeft, top: coverTop, width: COVER_W, height: COVER_H, borderRadius: 18, border: `5px solid ${INK.black}`, objectFit: 'cover'}}
			/>
			<svg width={QR_SIZE} height={QR_SIZE} viewBox={`0 0 ${QR_SIZE} ${QR_SIZE}`} style={{position: 'absolute', left: qrLeft, top: qrTop}}>
				<rect width={QR_SIZE} height={QR_SIZE} fill="#fff" />
				{rects}
			</svg>
			<div style={{position: 'absolute', left: 0, width: W, top: coverTop + COVER_H + 60, textAlign: 'center', fontFamily: 'Consolas, "Courier New", monospace', fontSize: 30, color: INK.gray}}>
				instagram.com/reel/DePwOM8S0_S
			</div>
		</AbsoluteFill>
	);
};
