const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

// Enable CORS
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

app.post('/update-data', (req, res) => {
  const data = req.body.value;
  console.log("Received a post request")
  // Write the data to a file
 
  const fs = require('fs');

    // Read the contents of the file
    const fileContents = fs.readFileSync('sensors.csv', 'utf8');

    // Split the contents into individual lines
    const lines = fileContents.split('\n');
    const data_lines = data.split('\n');
    lines.forEach((line, index) => {
        const parts = line.split(',');
        // Iterate over the lines to find and update the values
        
        data_lines.forEach((data_line, data_index) => {
          const data_parts = data_line.split(',');
          // Check the identifier and update the corresponding value
          if (parts[0] === data_parts[0]) {
              
              if(parts[0]=='E') parts[1] = (data_parts[1]/3.5).toFixed(1);
              else parts[1] = (data_parts[1]*0.836/3.5).toFixed(1);
              console.log("update "+parts[0]+' with '+parts[1])
          }

          // Join the parts back into a line
          lines[index] = parts.join(',');
        });
    });

    // Write the updated contents back to the file
    fs.writeFileSync('sensors.csv', lines.join('\n'));
  res.sendStatus(200);
});

// Serve the HTML file
app.get('/', (req, res) => {
  const htmlPath = path.join(__dirname, 'index.html');
  res.sendFile(htmlPath);
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
