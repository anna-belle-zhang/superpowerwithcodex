const express = require('express');
const app = express();

app.get('/status', (req, res) => {
  // TODO: implement — must include X-Version: 1 response header
  res.status(501).json({ error: 'Not implemented' });
});

if (require.main === module) {
  app.listen(3000, () => console.log('Server running on port 3000'));
}

module.exports = app;
