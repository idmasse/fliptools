import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [activePage, setActivePage] = useState('onboarding');
  const [theme, setTheme] = useState('green'); // 'green' or 'modern'

  // Apply theme class to body
  useEffect(() => {
    document.body.className = `theme-${theme}`;

    // Clean up function
    return () => {
      document.body.className = '';
    };
  }, [theme]);

  // Define CSV template content with required and optional fields
  const csvTemplateContent = `brand_name,companyName,mainContactName,vendorMainContactEmail,description,foundedInYear,countryOfOrigin,instagramUrl,websiteUrl,mainContactPhone
Test Brand 2,Brand Pitt LLC,Hugh Jazz,hugh@somebrand.com,Un-sustainable fashion is what we do best,2018,United States,instagram.com/unsustainablefashion,somebrand.com,+18005678901`;

  const onFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage('');
    setResults(null);
    setError(null);
  };

  const downloadTemplate = () => {
    const blob = new Blob([csvTemplateContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', 'brand_template.csv');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url); // Clean up
  };

  const toggleTheme = () => {
    setTheme(theme === 'green' ? 'modern' : 'green');
  };

  const onFileUpload = () => {
    if (!file) {
      setMessage("Please select a CSV file.");
      return;
    }

    // Validate file type
    if (!file.name.endsWith('.csv')) {
      setError("Please select a CSV file.");
      return;
    }

    setIsLoading(true);
    setMessage("Uploading and processing file...");
    setResults(null);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload", {
      method: "POST",
      body: formData,
    })
      .then(response => {
        if (!response.ok) {
          return response.json().then(data => {
            throw new Error(data.error || "Server error");
          });
        }
        return response.json();
      })
      .then(data => {
        setMessage("File processed successfully.");
        setResults(data);
        console.log("Upload results:", data);
      })
      .catch(error => {
        setError(error.message || "Error uploading file");
        console.error("Error:", error);
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  const renderContent = () => {
    switch (activePage) {
      case 'onboarding':
        return (
          <>
            <h1>Brand Onboarding</h1>
            <p className="tagline">Create brand profiles in bulk</p>

            <div className="App-card">
              <h2>Upload CSV File</h2>
              <p className="instruction">Please upload a CSV file with the required fields.
                {/* Please upload a CSV file with the required fields: <code>brand_name</code>, <code>companyName</code>, <code>mainContactName</code>, and <code>vendorMainContactEmail</code>.
                <br />
                Optional fields include: <code>description</code>, <code>foundedInYear</code>, <code>countryOfOrigin</code>, <code>instagramUrl</code>, <code>websiteUrl</code>, and <code>mainContactPhone</code>. */}
              </p>
              <div className="upload-container">
                <input
                  type="file"
                  accept=".csv"
                  onChange={onFileChange}
                  disabled={isLoading}
                />
                <button
                  onClick={onFileUpload}
                  disabled={!file || isLoading}
                >
                  {isLoading ? 'Processing...' : 'Upload'}
                </button>
              </div>

              {message && (
                <div className="message">{message}</div>
              )}

              {error && (
                <div className="error-message">{error}</div>
              )}
            </div>

            {results && results.length > 0 && (
              <div className="App-card results-container">
                <h3>Processing Results</h3>
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>Brand</th>
                      <th>Status</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((item, index) => (
                      <tr key={index}>
                        <td>{item.brand || 'Unknown'}</td>
                        <td>
                          {item.error ? (
                            <span className="error-text">Error</span>
                          ) : (
                            <span className="success-text">Success</span>
                          )}
                        </td>
                        <td>
                          {item.error ? (
                            <div className="error-details">
                              <span className="error-text">{item.error}</span>
                            </div>
                          ) : (
                            <pre className="result-data">
                              {JSON.stringify(item.result, null, 2)}
                            </pre>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="App-card csv-template-info">
              <h3>CSV Template</h3>
              <p className="template-instruction">
                <strong>Required fields:</strong> brand_name, companyName, mainContactName, vendorMainContactEmail, websiteUrl
                <br />
                <strong>Optional fields:</strong> description, foundedInYear, countryOfOrigin, instagramUrl, mainContactPhone
                <br /><br />
                If optional columns are missing or fields are empty, default values will be used.
                <br /><br />
                <strong>Note:</strong> Phone numbers must be in international format with a plus sign (e.g., +18005678910).
              </p>
              <div className="template-actions">
                <button onClick={downloadTemplate}>
                  Download Template
                </button>
                {/* <button
                  className="copy-button"
                  onClick={() => {
                    navigator.clipboard.writeText(csvTemplateContent);
                  }}
                >
                  Copy Template to Clipboard
                </button> */}
              </div>
            </div>
          </>
        );
      case 'dashboard':
        return (
          <>
            <h1>Thing 2</h1>
            <p className="tagline">Something else eventually</p>
            <div className="App-card">
              <h2>Coming...sometime</h2>
              <p>Some other thing that will do things that suck doing manually.</p>
            </div>
          </>
        );
      case 'settings':
        return (
          <>
            <h1>Tool 3</h1>
            <p className="tagline">Something else eventually</p>
            <div className="App-card">
              <h2>Coming...eventually</h2>
              <p>Some other OTHER thing that will do things that suck doing manually.</p>
            </div>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <div className={`App theme-${theme}`}>
      <header className="App-header">
        <div className="App-header-left">
          <img src="/flip-black.png" alt="Flip Logo" className="App-logo" />
          <span className="App-header-tagline">This is gonna be good®</span>
        </div>
        <div className="App-header-right">
          <nav className="App-nav">
            <button
              className={activePage === 'onboarding' ? 'nav-button active' : 'nav-button'}
              onClick={() => setActivePage('onboarding')}
            >
              Create Brands
            </button>
            <button
              className={activePage === 'dashboard' ? 'nav-button active' : 'nav-button'}
              onClick={() => setActivePage('dashboard')}
            >
              Tool 2
            </button>
            <button
              className={activePage === 'settings' ? 'nav-button active' : 'nav-button'}
              onClick={() => setActivePage('settings')}
            >
              Tool 3
            </button>
          </nav>
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === 'green' ? 'light' : 'green'} theme`}
          >
            {theme === 'green' ? 'Light Theme' : 'Green Theme'}
          </button>
        </div>
      </header>
      <div className="App-body">
        <main className="App-main">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default App;