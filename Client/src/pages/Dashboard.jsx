import React, { useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { BarChart3, FileCheck2, ShieldAlert, ArrowLeft, Download } from 'lucide-react'
import { jsPDF } from 'jspdf'
import html2canvas from 'html2canvas'

export default function Dashboard() {
  const location = useLocation()
  const navigate = useNavigate()
  const [isDownloading, setIsDownloading] = useState(false)

  const dashboardData = useMemo(() => {
    const stateResult = location.state?.result
    if (stateResult) {
      return stateResult
    }

    const stored = sessionStorage.getItem('predictionResult')
    return stored ? JSON.parse(stored) : null
  }, [location.state])

  const fileName = location.state?.fileName || sessionStorage.getItem('uploadedFileName') || 'Uploaded CSV'

  // Format prediction data for display
  const formattedPrediction = useMemo(() => {
    if (!dashboardData?.prediction) return null
    
    const pred = dashboardData.prediction
    if (Array.isArray(pred)) {
      if (pred.length === 0) return null
      
      // Check if it's RUL data (has 'rul' field)
      if (pred[0]?.rul !== undefined) {
        return pred.map((p, idx) => `[${idx + 1}] RUL: ${p.rul} ${p.unit || 'cycles'}`)
      }
      // Check if it's classification data (has 'fault_code' or 'fault_name')
      if (pred[0]?.fault_code !== undefined || pred[0]?.fault_name !== undefined) {
        return pred.map((p, idx) => `[${idx + 1}] ${p.fault_name || p.fault_code}`)
      }
      // Generic format
      return pred.map((p, idx) => `[${idx + 1}] ${JSON.stringify(p)}`)
    }
    return JSON.stringify(pred, null, 2)
  }, [dashboardData])

  // Get CSV data from sessionStorage if available
  const csvData = useMemo(() => {
    const stored = sessionStorage.getItem('uploadedCsvData')
    return stored ? stored : null
  }, [])

  const generatePDF = async () => {
    setIsDownloading(true)
    try {
      const pdf = new jsPDF('p', 'mm', 'a4')
      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()
      const margin = 15

      // Add footer to all pages
      const totalPages = pdf.internal.pages.length
      pdf.setFontSize(8)
      pdf.setTextColor(120, 120, 120)
      
      // PAGE 1: Results
      pdf.setFontSize(20)
      pdf.text('Prediction Report', margin, 20)
      
      pdf.setFontSize(11)
      pdf.setTextColor(80, 80, 80)
      let yPos = 35

      // Model name
      pdf.setFontSize(12)
      pdf.setTextColor(0, 0, 0)
      pdf.text(`Model: ${dashboardData?.model || 'Unknown'}`, margin, yPos)
      yPos += 8

      // File name
      pdf.setFontSize(10)
      pdf.setTextColor(80, 80, 80)
      pdf.text(`File: ${fileName}`, margin, yPos)
      yPos += 8

      // Rows processed
      pdf.text(`Rows Processed: ${dashboardData?.rows || 0}`, margin, yPos)
      yPos += 12

      // Summary
      pdf.setFontSize(12)
      pdf.setTextColor(0, 0, 0)
      pdf.text('Summary:', margin, yPos)
      yPos += 6
      pdf.setFontSize(10)
      pdf.setTextColor(80, 80, 80)
      const summaryWrapped = pdf.splitTextToSize(dashboardData?.summary || 'No summary available', pageWidth - 2 * margin)
      pdf.text(summaryWrapped, margin, yPos)
      yPos += summaryWrapped.length * 5 + 8

      // Risk Level (if available)
      if (dashboardData?.risk_level) {
        pdf.setFontSize(12)
        pdf.setTextColor(0, 0, 0)
        pdf.text('Risk Level:', margin, yPos)
        yPos += 6
        pdf.setFontSize(11)
        const riskColor = dashboardData.risk_level.includes('Low') ? [0, 128, 0] : 
                         dashboardData.risk_level.includes('Medium') ? [255, 165, 0] : [192, 0, 0]
        pdf.setTextColor(...riskColor)
        pdf.text(dashboardData.risk_level, margin, yPos)
        yPos += 10
      }

      // Predictions
      yPos += 4
      pdf.setFontSize(12)
      pdf.setTextColor(0, 0, 0)
      pdf.text('Predictions:', margin, yPos)
      yPos += 6
      pdf.setFontSize(10)
      pdf.setTextColor(80, 80, 80)
      
      if (formattedPrediction) {
        const predArray = Array.isArray(formattedPrediction) ? formattedPrediction : [formattedPrediction]
        const predWrapped = pdf.splitTextToSize(predArray.join('\n'), pageWidth - 2 * margin)
        const predHeight = predWrapped.length * 4
        
        if (yPos + predHeight > pageHeight - margin) {
          pdf.addPage()
          yPos = margin
        }
        pdf.text(predWrapped, margin, yPos)
      }

      // PAGE 2: CSV Data (if available)
      if (csvData) {
        pdf.addPage()
        pdf.setFontSize(16)
        pdf.setTextColor(0, 0, 0)
        pdf.text('Input Data', margin, 20)
        
        yPos = 30
        pdf.setFontSize(9)
        pdf.setTextColor(80, 80, 80)
        
        // Parse and display CSV in a more compact format
        const lines = csvData.trim().split('\n').slice(0, 50) // Limit to first 50 rows
        const csvWrapped = pdf.splitTextToSize(lines.join('\n'), pageWidth - 2 * margin)
        pdf.text(csvWrapped, margin, yPos)
        
        // Add note if data was truncated
        if (csvData.trim().split('\n').length > 50) {
          yPos = pageHeight - 15
          pdf.setFontSize(8)
          pdf.setTextColor(120, 120, 120)
          pdf.text('(Showing first 50 rows of data)', margin, yPos)
        }
      }

      // Add footer to all pages
      const pageCount = pdf.getNumberOfPages()
      for (let i = 1; i <= pageCount; i++) {
        pdf.setPage(i)
        pdf.setFontSize(8)
        pdf.setTextColor(150, 150, 150)
        pdf.text(
          'Made with ❤️ by shivamm-verma/AAI_Risk-analysis_Fault-Prediction',
          pageWidth / 2,
          pageHeight - 8,
          { align: 'center' }
        )
      }

      // Download the PDF
      pdf.save(`prediction-report-${Date.now()}.pdf`)
    } catch (error) {
      console.error('PDF generation failed:', error)
      alert('Failed to generate PDF. Please try again.')
    } finally {
      setIsDownloading(false)
    }
  }

  if (!dashboardData) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12">
        <div className="rounded-2xl border border-blue-100 bg-white p-10 text-center shadow-sm">
          <ShieldAlert className="mx-auto h-10 w-10 text-blue-900" />
          <h1 className="mt-4 text-3xl font-bold text-blue-900">No results yet</h1>
          <p className="mt-2 text-gray-600">
            Upload a CSV file in the tools section to generate predictions.
          </p>
          <button
            onClick={() => navigate('/tools')}
            className="mt-6 inline-flex items-center gap-2 rounded-lg bg-blue-800 px-5 py-3 text-white font-semibold hover:bg-blue-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Tools
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-slate-50 min-h-screen flex flex-col">
      <div className="flex-1 max-w-7xl mx-auto px-4 py-12">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-4xl font-bold text-blue-900">Prediction Dashboard</h1>
            <p className="mt-2 text-gray-700">
              Results generated for: <span className="font-semibold">{fileName}</span>
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={generatePDF}
              disabled={isDownloading}
              className="inline-flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-white font-semibold hover:bg-green-700 disabled:opacity-70 disabled:cursor-not-allowed"
            >
              <Download className="h-4 w-4" />
              {isDownloading ? 'Generating...' : 'Download PDF'}
            </button>
            <button
              onClick={() => navigate('/tools')}
              className="inline-flex items-center gap-2 rounded-lg border border-blue-200 bg-white px-4 py-2 text-blue-900 font-semibold hover:bg-blue-50"
            >
              <ArrowLeft className="h-4 w-4" />
              Upload another
            </button>
          </div>
        </div>

        <div className="mt-10 grid gap-6 lg:grid-cols-3">
          <div className="rounded-2xl border border-blue-100 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-3 text-blue-900">
              <BarChart3 className="h-6 w-6" />
              <h2 className="text-lg font-semibold">Summary</h2>
            </div>
            <p className="mt-3 text-sm text-gray-600">
              {dashboardData?.summary || 'Summary details will appear here once the model responds.'}
            </p>
          </div>

          <div className="rounded-2xl border border-blue-100 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-3 text-blue-900">
              <FileCheck2 className="h-6 w-6" />
              <h2 className="text-lg font-semibold">Model Used</h2>
            </div>
            <p className="mt-3 text-sm font-mono text-gray-700">
              {dashboardData?.model || 'Unknown'}
            </p>
            <p className="mt-2 text-xs text-gray-500">
              Processed {dashboardData?.rows || 0} rows
            </p>
          </div>

          <div className="rounded-2xl border border-blue-100 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-3 text-blue-900">
              <ShieldAlert className="h-6 w-6" />
              <h2 className="text-lg font-semibold">Risk Level</h2>
            </div>
            <p className="mt-3 text-lg font-bold text-gray-700">
              {dashboardData?.risk_level ? (
                <span className={
                  dashboardData.risk_level.includes('Low') ? 'text-green-600' :
                  dashboardData.risk_level.includes('Medium') ? 'text-yellow-600' :
                  'text-red-600'
                }>
                  {dashboardData.risk_level}
                </span>
              ) : (
                'N/A'
              )}
            </p>
          </div>
        </div>

        {/* Predictions Section */}
        <div className="mt-8 rounded-2xl border border-blue-100 bg-white p-6 shadow-sm">
          <h3 className="text-xl font-semibold text-blue-900 mb-4">Predictions</h3>
          <div className="bg-slate-50 rounded-lg p-4 max-h-80 overflow-auto">
            {formattedPrediction ? (
              <div className="text-sm text-gray-700 font-mono">
                {Array.isArray(formattedPrediction) ? (
                  formattedPrediction.map((pred, idx) => (
                    <div key={idx} className="py-1 border-b border-blue-100 last:border-b-0">
                      {pred}
                    </div>
                  ))
                ) : (
                  <pre>{formattedPrediction}</pre>
                )}
              </div>
            ) : (
              <p className="text-gray-500">No prediction data available.</p>
            )}
          </div>
        </div>

        {/* Raw Response Section */}
        <div className="mt-8 rounded-2xl border border-blue-100 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">Raw API Response</h3>
          <pre className="max-h-96 overflow-auto rounded-lg bg-slate-900 p-4 text-xs text-slate-100">
            {JSON.stringify(dashboardData, null, 2)}
          </pre>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center py-8 border-t border-blue-100">
          <p className="text-sm text-gray-600">
            Made with ❤️ by{' '}
            <a 
              href="https://github.com/shivamm-verma/AAI_Risk-analysis_Fault-Prediction" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 font-semibold"
            >
              shivamm-verma/AAI_Risk-analysis_Fault-Prediction
            </a>
          </p>
        </footer>
      </div>
    </div>
  )
}
