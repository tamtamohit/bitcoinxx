import React from 'react';
import { render } from 'react-dom';

var Parent = React.createClass({
    render : function(){
        return(
            <div>


                <signup/>


            </div>
        )
    }
})



var signup = React.createClass({
    render : function(){
        return(
            <div class="content">

                <div id="buttons">
                    <p id="loginbutton">Login</p>
                    <p id="signupbutton">Sign Up</p>
                </div>
                <div id="signup">
                    <input type="text" id="first" placeholder="First Name">
                    <input type="text" id="last" placeholder="Last Name">
                    <input type="text" id="email" placeholder="Email">
                    <input type="password" id="password" placeholder="Password">
                    <input type="password" id="confirm" placeholder="Confirm Password">
                    <button id="send">Create Account</button>
                </div>
            </div>
        )
    }
})

ReactDOM.render(<Parent/>,document.getElementById('space'))