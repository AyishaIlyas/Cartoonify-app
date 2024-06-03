import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; 

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [cartoon, setCartoon] = useState(null);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) return; // Handle if no file is selected

    const reader = new FileReader();
    reader.onloadend = async () => {
      const base64String = reader.result.replace('data:', '').replace(/^.+,/, '');

      try {
        const response = await axios.post('http://localhost:5000/cartoonify', {
          image: base64String,
        });
        setCartoon(`data:image/jpeg;base64,${response.data.cartoon}`);
      } catch (error) {
        console.error('Error:', error);
        // Handle errors
      }
    };
    reader.readAsDataURL(selectedFile);
  };

  return (
    <div className="App">
      <h1>Cartoonify Image</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button type="submit">Upload and Cartoonify</button>
      </form>
      {cartoon && <img src={cartoon} alt="Cartoonified" />}
    </div>
  );
}

export default App;

