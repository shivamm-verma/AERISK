import React, { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import {
  UploadCloud,
  FileText,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
} from 'lucide-react'

function Tools() {
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const apiBaseUrl = useMemo(() => {
    return import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
  }, [])

  const resetError = () => setErrorMessage('')

  const validateCsv = (file) => {
    if (!file) {
      return 'Please select a CSV file.'
    }

    const isCsvExtension = file.name.toLowerCase().endsWith('.csv')
    const isCsvMime = file.type === 'text/csv' || file.type === 'application/vnd.ms-excel'

    if (!isCsvExtension && !isCsvMime) {
      return 'Only CSV files are allowed.'
    }

    return ''
  }

  const handleFileChange = (event) => {
    resetError()
    const file = event.target.files?.[0]
    const validationError = validateCsv(file)

    if (validationError) {
      setSelectedFile(null)
      setErrorMessage(validationError)
      event.target.value = ''
      return
    }

    setSelectedFile(file)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    resetError()

    const validationError = validateCsv(selectedFile)
    if (validationError) {
      setErrorMessage(validationError)
      return
    }

    try {
      setIsSubmitting(true)

      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await axios.post(`${apiBaseUrl}/predict`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      const result = response.data
      sessionStorage.setItem('predictionResult', JSON.stringify(result))

      navigate('/dashboard', {
        state: {
          result,
          fileName: selectedFile.name,
        },
      })
    } catch (error) {
      const message =
        error?.response?.data?.message ||
        error?.message ||
        'Unable to process the CSV right now. Please try again.'
      setErrorMessage(message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-6">
            <div className="flex items-center gap-3 text-blue-900">
              <ShieldCheck className="w-9 h-9" />
              <div>
                <h1 className="text-4xl font-bold">Risk Analysis Toolkit</h1>
                <p className="text-lg text-gray-700 mt-2">
                  Upload a single CSV file to generate fault predictions and risk insights.
                </p>
              </div>
            </div>

            <div className="rounded-2xl border border-blue-100 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-semibold text-blue-900 mb-2">How it works</h2>
              <ul className="space-y-3 text-gray-700">
                <li className="flex items-start gap-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-blue-600" />
                  Prepare a clean CSV with system telemetry and fault signals.
                </li>
                <li className="flex items-start gap-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-blue-600" />
                  Submit the CSV to the ML model for prediction.
                </li>
                <li className="flex items-start gap-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-blue-600" />
                  View results instantly on the dashboard with actionable insights.
                </li>
              </ul>
            </div>

            <div className="rounded-2xl bg-gradient-to-br from-blue-600 to-blue-900 p-6 text-white shadow-lg">
              <div className="flex items-start gap-4">
                <UploadCloud className="w-10 h-10" />
                <div>
                  <h3 className="text-xl font-semibold">Upload Requirements</h3>
                  <p className="text-sm text-blue-100 mt-1">
                    Only one CSV file can be uploaded at a time. Maximum 50MB recommended.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-blue-100 bg-white p-6 shadow-sm">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="flex items-center gap-3 text-blue-900">
                <FileText className="w-7 h-7" />
                <h2 className="text-2xl font-semibold">Upload CSV</h2>
              </div>

              <label className="block">
                <span className="text-sm font-medium text-gray-700">CSV file</span>
                <div className="mt-3 rounded-xl border-2 border-dashed border-blue-200 bg-blue-50/60 p-6 text-center">
                  <input
                    type="file"
                    accept=".csv,text/csv"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-gray-700 file:mr-4 file:rounded-lg file:border-0 file:bg-blue-700 file:px-4 file:py-2 file:text-white hover:file:bg-blue-800"
                  />
                  <p className="mt-2 text-xs text-gray-500">
                    Drag and drop is supported. CSV only.
                  </p>
                </div>
              </label>

              {selectedFile && (
                <div className="rounded-xl border border-blue-100 bg-blue-50 p-4 text-sm text-blue-900">
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-semibold">Selected:</span>
                    <span className="truncate text-gray-700">{selectedFile.name}</span>
                  </div>
                </div>
              )}

              {errorMessage && (
                <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  <AlertTriangle className="mt-0.5 h-4 w-4" />
                  <span>{errorMessage}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-blue-800 px-6 py-3 text-white font-semibold shadow-md transition hover:bg-blue-900 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {isSubmitting ? 'Uploading...' : 'Send to ML Model'}
                <ArrowRight className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Tools
