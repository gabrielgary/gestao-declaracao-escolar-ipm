import favicon from '../../../assets/images/favicon.ico'
import style from './HeaderClient.module.css'
import {FaUser} from 'react-icons/fa6'
export default function HeaderClient(){
    return(
        <div className={style.HeaderClient}>
            <div className={style.LogoSchool}>
                <img src={favicon} alt="" />
                <h1>INSTITUTO POLITÉCNICO <br /> DO MAIOMBE</h1>
            </div>
            <div className={style.DataUser}>
             
                    <div className={style.img}>
                      
                            <FaUser/>
                       
                    </div>
                    
                
            </div>
        </div>
    )
}