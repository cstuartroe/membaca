import React, { Component } from "react";
import {User} from "./models";
import {Link, Navigate} from "react-router-dom";

type Props = {
    user: User,
}

type State = {
}

export default class AdminPowers extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
        };
    }


    render() {
        if (!this.props.user.is_superuser) {
            return <Navigate to="/"/>;
        }

        return (
            <div className="col-12 col-md-6 offset-md-3">
                <div className="row">
                    <div className="col-6">
                        <a href="/admin/">
                            <div className="big button">
                                Django admin
                            </div>
                        </a>
                    </div>
                    <div className="col-6">
                        <Link to="/add_document">
                            <div className="big button">
                                Add document
                            </div>
                        </Link>
                    </div>
                </div>
            </div>
        );
    }
}
