import React, { Component } from "react";
import { Navigate } from "react-router-dom"
import { UserState } from "./types";

type Props = {
    user_state: UserState,
}

type State = {
}

export default class Home extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
        };
    }


    render() {
        if (this.props.user_state.user === null) {
            window.location.href = "/google_sso/login/?next=/";
            return null;
        }

        else if (this.props.user_state.current_language === null) {
            return <Navigate to="/choose_language"/>;
        }

        else {
            return <Navigate to="/dashboard"/>;
        }
    }
}
