import type { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  const isProduction = process.env.VERCEL_ENV === 'production';

  if (isProduction) {
    return {
      rules: [{ userAgent: '*', allow: '/' }],
    };
  }

  return {
    rules: [{ userAgent: '*', disallow: '/' }],
  };
}
