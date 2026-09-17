export type Person = {
  name: string
}


export type Item = {
  name: string
  price: string
  quantity: number | ""
  shared_by: Person[]
}


export type Receipt = {
  items: Item[]
  tax: string
  tip: string
  people: Person[]
}


export type SplitResult = {
  [name: string]: number
}