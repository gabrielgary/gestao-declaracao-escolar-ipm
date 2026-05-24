import {useState} from "react";
export default function Example(valores){
    const [values, setValues]=useState(valores);
    const handleChange=(evento)=>{
        setValues({...values,[evento.target.name]:evento.target.value})
    }
    return [values, handleChange]
}