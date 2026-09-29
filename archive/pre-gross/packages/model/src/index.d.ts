export * from './types.js';
export const MODEL_VERSION: 'paper-i-v1';
export interface ValidationIssue {
  path: string;
  message: string;
}
export function validateScenario(value: unknown): {
  ok: boolean;
  errors: ValidationIssue[];
};
export function roundTripScenario<T>(scenario: T): T;
