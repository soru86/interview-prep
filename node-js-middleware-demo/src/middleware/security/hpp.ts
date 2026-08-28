import hpp from 'hpp';

/**
 * HTTP Parameter Pollution protection — keeps only the last value for
 * duplicated query/body keys that attackers use to confuse parsers.
 */
export const hppMiddleware = hpp({
  whitelist: ['tags', 'sort'],
});
