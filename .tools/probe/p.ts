import { test } from 'node:test';
import assert from 'node:assert';
type X = { a: number };
test('ts directo', () => { const x: X = { a: 1 }; assert.equal(x.a, 1); });

