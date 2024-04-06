import React, { Component } from "react";

type Props = {
}

type State = {
}

export default class LoggedOutHome extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
        };
    }


    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-12 col-md-8 offset-md-2">
                        <p style={{textAlign: "center", paddingTop: "30vh"}}>
                            You are logged out.
                        </p>

                        <a href="/google_sso/login/" target="_blank">
                            <div className="big button">
                                Log in
                            </div>
                        </a>
                    </div>
                </div>
            </div>
        );
    }
}
