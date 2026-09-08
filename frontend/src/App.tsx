import './App.css'
import { useState } from 'react'
import type { Person, Receipt, SplitResult } from './types'

const API_URL = import.meta.env.VITE_API_URL

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [receipt, setReceipt] = useState<Receipt | null>(null)
  const [personName, setPersonName] = useState("")
  const [splitResult, setSplitResult] = useState<SplitResult | null>(null)
  const [errorMessage, setErrorMessage] = useState("")
  const [isUploading, setIsUploading] = useState(false)
  const [isCalculating, setIsCalculating] = useState(false)

  const subtotalCents = receipt ? receipt.items.reduce((sum, item) => {
      return sum + toCents(item.price)
    }, 0) : 0
  
  const totalCents = receipt ? subtotalCents + toCents(receipt.tax) + toCents(receipt.tip) : 0

  async function handleUpload() {
    if (!selectedFile) {
      return
    }

    const formData = new FormData()
    formData.append("file", selectedFile)

    setIsUploading(true)
    try {
      const response = await fetch(
        `${API_URL}/receipts/extract`,
        {
          method: "POST",
          body: formData
        }
      )
    

      if (!response.ok){
          const errorData = await response.json()
          setErrorMessage(errorData.detail || "Unable to extract receipt.")
          return
      }

      const data = await response.json()
      setReceipt(data)
      setErrorMessage("")
    } catch {
      setErrorMessage("Unable to connect to server.")
    } finally {
      setIsUploading(false)
    }
  }

  async function handleCalculate() {
    if (!receipt) {
      return
    }
  
    const hasUnassignedItem = receipt.items.some(
      item => item.shared_by.length === 0
    )

    if (hasUnassignedItem) {
      setErrorMessage("Assign at least one person to every item.")
      return
    }

    const receiptToCalculate = {
      ...receipt,
      subtotal: fromCents(subtotalCents),
      total: fromCents(totalCents)
    }
    
    setIsCalculating(true)
    try {
      const response = await fetch(
        `${API_URL}/receipts/calculate`,
         {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(receiptToCalculate)
          }
        )

      if (!response.ok){
        const errorData = await response.json()
        setErrorMessage(errorData.detail || "Unable to calculate receipt.")
        return
      }
    
      const data = await response.json()
      setSplitResult(data)
      setErrorMessage("")
    } catch {
      setErrorMessage("Unable to connect to server.")
    } finally {
      setIsCalculating(false)
    }
  }

  function updateItem(index: number, field: "name" | "price", value: string) {
    if (!receipt) {
      return
    }
    
    const updatedItems = [...receipt.items]

    updatedItems[index] = {
      ...updatedItems[index],
      [field]: value
    }

    setReceipt({
      ...receipt,
      items: updatedItems
    })

    setSplitResult(null)
  }

  function updateReceipt(field: "tax" | "tip", value: string) {
    if (!receipt) {
      return
    }

    setReceipt({
      ...receipt,
      [field]: value
    })

    setSplitResult(null)
  }

  function toCents(value: string) {

    return Math.round(Number(value) * 100)

  }

  function fromCents(value: number) {
    return (value / 100).toFixed(2)
  }

  function addPerson() {
    if (!receipt || !personName.trim()) {
      return
    }

    const name = personName.trim()

    const personExists = receipt.people.some(
      person => person.name.toLowerCase() === name.toLowerCase()
    )

    if (personExists) {
      setErrorMessage("A person with that name already exists.")
      return
    }

    const newPerson: Person = {
      name: name
    }

    setReceipt({
      ...receipt,
      people: [...receipt.people, newPerson]
    })

    setPersonName("")
    setErrorMessage("")

  }

  function togglePersonForItem(itemIndex: number, person: Person){
    if (!receipt) {
      return
    }

    const updatedItems = [...receipt.items]
    const item = updatedItems[itemIndex]

    const isAssigned = item.shared_by.some(
      assignedPerson => assignedPerson.name === person.name
    )

    updatedItems[itemIndex] = {
      ...item,
      shared_by: isAssigned
      ? item.shared_by.filter(
          assignedPerson => assignedPerson.name !== person.name
        )
      : [...item.shared_by, person]
    }

    setReceipt({
      ...receipt,
      items: updatedItems
    })
  }

  return (
    <div className = "app">
      <h1>Receipt Splitter</h1>
      <p>Upload a receipt.</p>
      <input 
        type = "file"
        accept = "image/*"
        onChange = {(event) => {
          const file = event.target.files?.[0]

          if (file) {
            setSelectedFile(file)
          }
        }}
      />

      <button 
        onClick = {handleUpload}
        disabled = {isUploading}
      >
        {isUploading ? "Extracting..." : "Upload"}
      </button>

      {errorMessage && (
        <p className = "error-message">
          {errorMessage}
        </p>
      )}

      {receipt && (
        <div className = "receipt-section">
          <h2>Receipt</h2>
          <div className = "item-header">
            <span>Item</span>
            <span>Price</span>
          </div>
          {receipt.items.map((item, index) => (
            <div className = "item" key = {index}>
              <div className = "item-fields">
                <input
                  value = {item.name}
                  onChange = {(event) => {
                    updateItem(index, "name", event.target.value)
                  }}
                />

                <input
                  type = "text"
                  value = {item.price}
                  onChange = {(event) => {
                    const value = event.target.value

                    if (/^\d*(\.\d{0,2})?$/.test(value)) {
                      updateItem(index, "price", event.target.value)
                    }
                  }}
                />
              </div>
              <div className = "item-people">
                {receipt.people.map((person) => {
                  const isChecked = item.shared_by.some(
                    assignedPerson => assignedPerson.name === person.name
                  )
                  return (
                    <label key = {person.name}>
                      <input
                        type = "checkbox"
                        checked = {isChecked}
                        onChange={() => {
                          togglePersonForItem(index, person)
                        }}
                      />
                      {person.name}
                    </label>
                  )
                })}
              </div>

            </div>
          ))}
          <div className = "total-row">
            <label>Subtotal:</label>
            <input value = {fromCents(subtotalCents)} readOnly/>
          </div>
          <div className = "total-row">
            <label>Tax:</label>
            <input
                type = "text"
                value = {receipt.tax}
                onChange = {(event) => {
                  const value = event.target.value

                  if (/^(\d+(\.\d{0,2})?)?$/.test(value)) {
                    updateReceipt("tax", event.target.value)
                  }

                }}
              />
          </div>
          <div className = "total-row">
            <label>Tip:</label>
            <input
                type = "text"
                value = {receipt.tip}
                onChange = {(event) => {
                  const value = event.target.value

                  if (/^(\d+(\.\d{0,2})?)?$/.test(value)) {
                    updateReceipt("tip", event.target.value)
                  }

                }}
              />
          </div>
          <div className = "total-row">
            <label>Total:</label>
            <input value = {fromCents(totalCents)} readOnly/>
          </div>
          <div>
            <h3>People</h3>

            <input
              value = {personName}
              onChange = {(event) => {
                setPersonName(event.target.value)
              }}
              placeholder = "Add name"
            />
            <button onClick = {addPerson}>
              Add Person
            </button>
            <div className = "people-list">
              {receipt.people.map((person, index) => (
                <span className = "person" key = {index}>{person.name} </span>
              ))}
            </div>
          </div>

          <button 
            className = "primary-button" 
            onClick = {handleCalculate}
            disabled = {isCalculating}
          >
            {isCalculating ? "Calculating..." : "Calculate"}
          </button>

        </div>
        
      )}
      {splitResult && (
        <div className = " split-section">
          <h2>Split</h2>

          {Object.entries(splitResult).map(([name, amount]) => (
            <div className = "split-row" key = {name}>
              <p>
                {name}: ${amount.toFixed(2)}
              </p>
            </div>
          ))}
        </div>
      )}

    </div>
  )
}

export default App
