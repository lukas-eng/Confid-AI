import { BrowserRouter, Route, Routes } from "react-router-dom"
import Formuini from "./Paginas/Formuini"
import Formuregi from "./Paginas/FormuRegis"

const App = () => (
    <BrowserRouter>
        <Routes>
            <Route exact path="/" element={<Formuini />} />
            <Route exact path="/registro" element={<Formuregi />} />
        </Routes>
    </BrowserRouter>
)
export default App