import { Link } from "react-router-dom";
import  './BoxMessage.css'
export default function BoxMessage({msm, setController}) {
    return (

        <div className="card-logaout">
            <div className="card">
                <div>
                    <h3>{msm}</h3>
                </div>
                <div className="option">
                    <Link to='public/logout' id="option-btn-logout-yes">Sim</Link>
                    <Link to='' id="option-btn-logout-no" onClick={
                        ()=>setController((prev)=>prev=!prev)
                    }>Não</Link>
                </div>
            </div>
        </div>
    )
}