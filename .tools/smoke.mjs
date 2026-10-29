import { createSystem } from '../apps/api/src/composition-root.ts';
const s = createSystem({ logLevel: 'error' });
console.log('modules:', s.registry.ids().join(', '));
console.log('facts:', s.facts.keys().length, '->', s.facts.keys().join(', '));
console.log('actions:', s.actions.types().join(', '));
console.log('rules:', s.ruleRepository.size(), '| subs:', s.bus.subscriptions().map(x=>x.id).join(', '));
