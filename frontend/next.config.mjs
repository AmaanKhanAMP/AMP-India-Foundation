function apiRemotePattern(apiUrl) {
  try {
    const u = new URL(apiUrl);
    const pattern = {
      protocol: u.protocol.replace(':', ''),
      hostname: u.hostname,
      pathname: '/uploads/**',
    };
    if (u.port) pattern.port = u.port;
    return pattern;
  } catch {
    return null;
  }
}

const apiUrl = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000').replace(
  /\/$/,
  ''
);
const fromEnv = apiRemotePattern(apiUrl);

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Next 15 defaults staleTimes.dynamic to 0, so every Home/Events click
  // refetches RSC from the origin. Keep a short client router cache so
  // internal navigation does not wait on Render again.
  experimental: {
    staleTimes: {
      dynamic: 30,
      static: 180,
    },
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
      },
      ...(fromEnv ? [fromEnv] : []),
      { protocol: 'http', hostname: 'localhost', port: '5000', pathname: '/uploads/**' },
      { protocol: 'http', hostname: '127.0.0.1', port: '5000', pathname: '/uploads/**' },
    ],
    // Cap at 1920 so retina 100vw never requests a 3840px variant from Render.
    deviceSizes: [640, 750, 828, 1080, 1200, 1600, 1920],
    imageSizes: [16, 32, 48, 64, 96, 128, 140, 256, 384],
    minimumCacheTTL: 86400,
  },
};

export default nextConfig;
