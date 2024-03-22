import React, { Component } from "react";
import {UserState} from "./types";
import LoggedInHeader from "./LoggedInHeader";
import {Navigate} from "react-router-dom";

type Props = {
    user_state: UserState,
    reloadUserState: () => void,
    clearLanguage: () => void,
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
        if ((this.props.user_state.current_language == null) || (this.props.user_state.user == null)) {
            return <Navigate to="/"/>;
        }

        return (
            <>
                <LoggedInHeader
                    user_state={this.props.user_state}
                    reloadUserState={this.props.reloadUserState}
                    clearLanguage={this.props.clearLanguage}/>
                Damshbord
            </>
        );
    }
}
