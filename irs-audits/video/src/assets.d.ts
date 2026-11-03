// Webpack emits a URL for these; TypeScript needs telling.
declare module '*.woff2' {
	const url: string;
	export default url;
}
