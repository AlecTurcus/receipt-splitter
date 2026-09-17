import './App.css'
import { useState, useEffect } from 'react'
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

  //Wake backend server when app loads to reduce cold start wait time
  useEffect(() => {
    fetch(`${API_URL}/wake`).catch(() => {})
  }, [])

  const subtotalCents = receipt
    ? receipt.items.reduce((sum, item) => {
        return sum + (toCents(item.price) * (item.quantity === "" ? 0 : item.quantity))
      }, 0)
    : 0
  
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
    

      if (!response.ok) {
          const errorData = await response.json()
          setErrorMessage(errorData.detail || "Unable to extract receipt.")
          return
      }

      const data = await response.json()
      setReceipt(data)
      setSplitResult(null)
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

    const hasMissingPrice = receipt.items.some(
      item => item.price === ""
    )

    if (hasMissingPrice) {
      setErrorMessage("Every item must have a price.")
      return
    }

    const hasInvalidQuantity = receipt.items.some(
      item => item.quantity === "" || item.quantity <= 0
    )

    if (hasInvalidQuantity) {
      setErrorMessage("Every item must have a quantity > 0.")
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
      tax: receipt.tax === "" ? "0.00" : receipt.tax,
      tip: receipt.tip === "" ? "0.00" : receipt.tip,
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

      if (!response.ok) {
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


  function updateQuantity(index: number, quantity: number | "") {
    if (!receipt) {
      return
    }

    const updatedItems = [...receipt.items]

    updatedItems[index] = {
      ...updatedItems[index],
      quantity: quantity
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
    setSplitResult(null)
  }


  function removePerson(name: string) {
    if (!receipt) {
      return
    }

    const updatedPeople = receipt.people.filter(
      person => person.name !== name
    )

    const updatedItems = receipt.items.map(item => ({
      ...item,
      shared_by: item.shared_by.filter(
        person => person.name !== name
      )
    }))

    setReceipt({
      ...receipt,
      people: updatedPeople,
      items: updatedItems
    })

    setSplitResult(null)
  }


  function togglePersonForItem(itemIndex: number, person: Person) {
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
    setSplitResult(null)
  }


  function addItem() {
    if (!receipt) {
      return
    }

    const newItem = {
      name: "",
      price: "",
      quantity: 1,
      shared_by: []
    }

    setReceipt({
      ...receipt,
      items: [...receipt.items, newItem]
    })

    setSplitResult(null)
  }

  function removeItem(index: number) {
    if (!receipt) {
      return
    }

    const updatedItems = receipt.items.filter(
      (_, itemIndex) => itemIndex !== index
    )

    setReceipt({
      ...receipt,
      items: updatedItems
    })

    setSplitResult(null)
  }


  return (
    <div className="app">
      <h1>Receipt Splitter</h1>
      <p>Upload a receipt.</p>
      <p className="startup">Note: First receipt upload may take longer while server is starting up.</p>
      <input 
        type="file"
        accept="image/*"
        onChange={(event) => {
          const file = event.target.files?.[0]

          if (file) {
            setSelectedFile(file)
          }
        }}
      />

      <button 
        onClick={handleUpload}
        disabled={isUploading}
      >
        {isUploading ? "Extracting..." : "Upload"}
      </button>

      {errorMessage && (
        <p className="error-message">
          {errorMessage}
        </p>
      )}

      {receipt && (
        <div className="receipt-section">
          <h2>Receipt</h2>
          <div className="item-header">
            <span>Qty</span>
            <span>Item</span>
            <span>Unit Price</span>
          </div>
          {receipt.items.map((item, index) => (
            <div className="item" key={index}>
              <div className="item-main">
                <div className="item-fields">
                  <input
                    type="text"
                    inputMode="numeric"
                    value={item.quantity}
                    onChange={(event) => {
                      const value = event.target.value

                      if (/^\d*$/.test(value)) {
                        updateQuantity(index, value === "" ? "" : Number(value))
                      }
                    }}
                  />

                  <input
                    value={item.name}
                    onChange={(event) => {
                      updateItem(index, "name", event.target.value)
                    }}
                  />

                  <input
                    type="text"
                    inputMode="numeric"
                    value={item.price}
                    onChange={(event) => {
                      const value = event.target.value

                      if (/^\d*(\.\d{0,2})?$/.test(value)) {
                        updateItem(index, "price", event.target.value)
                      }
                    }}
                  />
                </div>
                
                <button 
                  className="remove-button" 
                  onClick={() => removeItem(index)}
                >
                  Remove
                </button>
              </div>
              <div className="item-people">
                {receipt.people.map((person) => {
                  const isChecked = item.shared_by.some(
                    assignedPerson => assignedPerson.name === person.name
                  )
                  return (
                    <label key={person.name}>
                      <input
                        type="checkbox"
                        checked={isChecked}
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
          <button 
            className="add-button"
            onClick={addItem}
          >
            Add Item
          </button>
          <div className="total-row">
            <label>Subtotal:</label>
            <input value={fromCents(subtotalCents)} readOnly/>
          </div>
          <div className="total-row">
            <label>Tax:</label>
            <input
                type="text"
                inputMode="numeric"
                value={receipt.tax}
                onChange={(event) => {
                  const value = event.target.value

                  if (/^(\d+(\.\d{0,2})?)?$/.test(value)) {
                    updateReceipt("tax", event.target.value)
                  }

                }}
              />
          </div>
          <div className="total-row">
            <label>Tip:</label>
            <input
                type="text"
                inputMode="numeric"
                value={receipt.tip}
                onChange={(event) => {
                  const value = event.target.value

                  if (/^(\d+(\.\d{0,2})?)?$/.test(value)) {
                    updateReceipt("tip", event.target.value)
                  }

                }}
              />
          </div>
          <div className="total-row">
            <label>Total:</label>
            <input value={fromCents(totalCents)} readOnly/>
          </div>
          <div>
            <h3>People</h3>

            <input
              value={personName}
              onChange={(event) => {
                setPersonName(event.target.value)
              }}
              placeholder="Add name"
            />
            <button onClick={addPerson}>
              Add Person
            </button>
            <div className="people-list">
              {receipt.people.map((person) => (
                <span className="person" key={person.name}>{person.name}
                <button className="remove-person-button" onClick={() => removePerson(person.name)}>
                  ✕
                </button>
                </span>
              ))}
            </div>
          </div>

          <button 
            className="primary-button" 
            onClick={handleCalculate}
            disabled={isCalculating}
          >
            {isCalculating ? "Calculating..." : "Calculate"}
          </button>

        </div>
        
      )}
      {splitResult && (
        <div className="split-section">
          <h2>Split</h2>

          {Object.entries(splitResult).map(([name, amount]) => (
            <div className="split-row" key={name}>
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
