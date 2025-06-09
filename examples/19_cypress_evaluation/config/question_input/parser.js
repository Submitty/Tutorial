const { time } = require('console');
const { exit } = require('process');

try {
  const fs = require('fs');
  const resultFile = 'result.txt';
  const jsonData = fs.readFileSync(
    './mochawesome-report/mochawesome.json',
    'utf8',
    (err, data) => {
      if (err) {
        console.error(err);
        return;
      }
      console.log(data);
    },
  );
  mochaObj = JSON.parse(jsonData);
  mochaStats = mochaObj['stats'];

  fs.writeFile(
    resultFile,
    JSON.stringify({
      total_tests: mochaStats['tests'],
      test_passed: mochaStats['passes'],
    }),
    (err) => {
      if (err) {
        console.log(err);
      }
    },
  );
} catch (err) {
  console.log('Error in parsing JSON file: ', err);
}

setTimeout(() => {
  exit(1);
}, 1000);
