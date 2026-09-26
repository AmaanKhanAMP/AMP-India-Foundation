function apiRemotePattern(apiUrl) {
  try {
    const u = new URL(apiUrl);
    const pattern = {
      protocol: u.protocol.replace(":", ""),
      hostname: u.hostname,
      pathname: "/uploads/**",
    };
    if (u.port) pattern.port = u.port;
    return pattern;
  } catch {
    return null;
  }
}

const apiUrl = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000").replace(
  /\/$/,
  ""
);
const fromEnv = apiRemotePattern(apiUrl);

/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      ...(fromEnv ? [fromEnv] : []),
      { protocol: "http", hostname: "localhost", port: "5000", pathname: "/uploads/**" },
      { protocol: "http", hostname: "127.0.0.1", port: "5000", pathname: "/uploads/**" },
    ],
  },
};

export default nextConfig;
