import { useState } from 'react'
import './App.css'

/*
 * LinkedIn Carousel → PDF Converter
 *
 * States:
 *   idle       — waiting for user to paste a URL
 *   validating — quick client-side check
 *   processing — backend is scraping + generating PDF
 *   done       — PDF ready for download
 *   error      — something went wrong
 */

const API_BASE = 'http://localhost:8000'

const STEPS = [
  { id: 'validate', label: 'Validating LinkedIn URL' },
  { id: 'browser',  label: 'Launching browser session' },
  { id: 'capture',  label: 'Capturing carousel slides' },
  { id: 'pdf',      label: 'Generating PDF document' },
]

function LinkedInIcon() {
  return (
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
    </svg>
  )
}

function LinkIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
    </svg>
  )
}

function FileIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  )
}

function DownloadIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

function AlertIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  )
}

function isValidLinkedInUrl(url) {
  return /^https?:\/\/(www\.)?linkedin\.com\/(posts|feed\/update|pulse)\//i.test(url.trim())
}

function App() {
  const [url, setUrl] = useState('')
  const [status, setStatus] = useState('idle')        // idle | processing | done | error
  const [activeStep, setActiveStep] = useState(-1)
  const [result, setResult] = useState(null)           // { pdfId, totalSlides, message } | { error }
  const [urlError, setUrlError] = useState('')

  const handleUrlChange = (e) => {
    setUrl(e.target.value)
    if (urlError) setUrlError('')
  }

  const handleConvert = async () => {
    const trimmed = url.trim()

    // Client-side validation
    if (!trimmed) {
      setUrlError('Please enter a LinkedIn post URL.')
      return
    }
    if (!isValidLinkedInUrl(trimmed)) {
      setUrlError('Please enter a valid LinkedIn post URL (e.g., https://www.linkedin.com/posts/...)')
      return
    }

    // Begin conversion
    setStatus('processing')
    setResult(null)
    setActiveStep(0)

    // Simulate step progression for UX
    // Step 0: validate (instant)
    setTimeout(() => setActiveStep(1), 600)   // browser launch
    setTimeout(() => setActiveStep(2), 2500)  // capturing
    // Step 3 (pdf) will be set when the API returns, or after a delay

    const pdfStepTimeout = setTimeout(() => setActiveStep(3), 15000)

    try {
      const response = await fetch(`${API_BASE}/api/convert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: trimmed }),
      })

      clearTimeout(pdfStepTimeout)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Server error (${response.status})`)
      }

      const data = await response.json()

      setActiveStep(3) // Generating PDF step
      // Brief pause to show the PDF step before completing
      await new Promise(r => setTimeout(r, 800))

      setStatus('done')
      setResult({
        pdfId: data.pdf_id,
        totalSlides: data.total_slides,
        message: data.message,
      })
    } catch (err) {
      clearTimeout(pdfStepTimeout)
      setStatus('error')
      setResult({ error: err.message || 'An unexpected error occurred.' })
    }
  }

  const handleDownload = () => {
    if (result?.pdfId) {
      window.open(`${API_BASE}/api/download/${result.pdfId}`, '_blank')
    }
  }

  const handleReset = () => {
    setUrl('')
    setStatus('idle')
    setActiveStep(-1)
    setResult(null)
    setUrlError('')
  }

  const isProcessing = status === 'processing'

  return (
    <>
      {/* Decorative orbs */}
      <div className="orb orb--1" />
      <div className="orb orb--2" />
      <div className="orb orb--3" />

      <div className="app-container">
        <div className="card">
          {/* Header */}
          <div className="header">
            <div className="header__icon">
              <LinkedInIcon />
            </div>
            <h1 className="header__title">Carousel → PDF</h1>
            <p className="header__subtitle">
              Paste a LinkedIn post link to download its carousel slides as a high-quality PDF.
            </p>
          </div>

          {/* URL Input */}
          <div className="input-group">
            <label htmlFor="linkedin-url">LinkedIn Post URL</label>
            <div className="input-wrapper">
              <LinkIcon />
              <input
                id="linkedin-url"
                className={`url-input ${urlError ? 'url-input--error' : ''}`}
                type="url"
                placeholder="https://www.linkedin.com/posts/..."
                value={url}
                onChange={handleUrlChange}
                onKeyDown={(e) => e.key === 'Enter' && !isProcessing && handleConvert()}
                disabled={isProcessing}
                autoComplete="off"
                spellCheck="false"
              />
            </div>
            {urlError && <p className="input-error">{urlError}</p>}
          </div>

          {/* Convert / Reset Button */}
          {status === 'done' || status === 'error' ? (
            <button className="btn btn--primary" onClick={handleReset}>
              <FileIcon />
              Convert Another Post
            </button>
          ) : (
            <button
              className="btn btn--primary"
              onClick={handleConvert}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <>
                  <span className="progress-spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                  Processing…
                </>
              ) : (
                <>
                  <FileIcon />
                  Convert to PDF
                </>
              )}
            </button>
          )}

          {/* Progress Steps */}
          {isProcessing && (
            <div className="progress-section">
              <div className="progress-card">
                <div className="progress-header">
                  <div className="progress-spinner" />
                  <span className="progress-header__text">Converting your carousel…</span>
                </div>
                <div className="progress-steps">
                  {STEPS.map((step, i) => {
                    let cls = 'step'
                    if (i < activeStep) cls += ' step--done'
                    else if (i === activeStep) cls += ' step--active'

                    return (
                      <div key={step.id} className={cls}>
                        <span className="step__indicator">
                          {i < activeStep ? (
                            <CheckIcon />
                          ) : (
                            i + 1
                          )}
                        </span>
                        <span>{step.label}</span>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Success Result */}
          {status === 'done' && result && (
            <div className="result-section">
              <div className="result-card result-card--success">
                <div className="result-info">
                  <div className="result-info__icon result-info__icon--success">
                    <CheckIcon />
                  </div>
                  <div className="result-info__text">
                    <h3>PDF Ready!</h3>
                    <p>{result.totalSlides} slides captured successfully.</p>
                  </div>
                </div>
                <button className="btn btn--success" onClick={handleDownload}>
                  <DownloadIcon />
                  Download PDF
                </button>
              </div>
            </div>
          )}

          {/* Error Result */}
          {status === 'error' && result && (
            <div className="result-section">
              <div className="result-card result-card--error">
                <div className="result-info">
                  <div className="result-info__icon result-info__icon--error">
                    <AlertIcon />
                  </div>
                  <div className="result-info__text">
                    <h3>Conversion Failed</h3>
                    <p>{result.error}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="footer">
          <p>For personal use only · Ensure you are logged into LinkedIn in the browser</p>
        </div>
      </div>
    </>
  )
}

export default App
