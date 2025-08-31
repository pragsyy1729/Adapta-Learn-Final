// Test the duration formatting
import { formatDuration } from '../src/utils/timeUtils';

console.log('Testing duration formatting:');
console.log('5 seconds:', formatDuration(5));
console.log('45 seconds:', formatDuration(45));
console.log('65 seconds (1m 5s):', formatDuration(65));
console.log('120 seconds (2m):', formatDuration(120));
console.log('3661 seconds (1h 1m 1s):', formatDuration(3661));
console.log('7200 seconds (2h):', formatDuration(7200));
console.log('90061 seconds (1d 1h 1m 1s):', formatDuration(90061));

// Test with the actual session data
const testSession = {
  duration_seconds: 197,
  duration_minutes: undefined
};

console.log('197 seconds formatted:', formatDuration(197));
