import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: [
    "use-stick-to-bottom",
    "streamdown",
    "react-markdown",
    "devlop",
    "hast-util-to-jsx-runtime",
    "comma-separated-tokens",
    "estree-util-is-identifier-name",
    "unist-util-visit",
    "unified",
    "vfile",
    "vfile-message",
    "unist-util-stringify-position",
    "remark-parse",
    "mdast-util-to-string",
    "micromark",
    "ccount",
    "property-information",
    "space-separated-tokens",
    "xtend",
    "hast-util-whitespace",
    "unist-util-position",
    "html-url-attributes",
    "mdast-util-from-markdown",
    "decode-named-character-reference",
    "micromark-util-chunked",
    "micromark-util-combine-extensions",
    "micromark-util-decode-numeric-character-reference",
    "micromark-util-encode",
    "micromark-util-normalize-identifier",
    "micromark-util-sanitize-uri",
    "micromark-util-character",
    "micromark-factory-space",
    "micromark-core-commonmark",
  ],
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "Cross-Origin-Opener-Policy",
            value: "same-origin-allow-popups",
          },
          {
            key: "Cross-Origin-Embedder-Policy",
            value: "unsafe-none",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
