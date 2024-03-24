import React, { Component } from "react";
import { LoggedInUserState } from "./types";
import {Link, Navigate} from "react-router-dom";

type Props = {
    user_state: LoggedInUserState,
}

type State = {
}

export default class Dashboard extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
        };
    }


    render() {
        const { user_state } = this.props;

        if (user_state.current_language === null) {
            return <Navigate to="/"/>;
        }

        return (
            <>
                {user_state.user.is_superuser && (
                    <div className="col-3 offset-3">
                        <Link to="/add_document">
                            <div className="big button">
                                Add document
                            </div>
                        </Link>
                    </div>
                )}
            </>
        );
    }
}
