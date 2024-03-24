import React, { Component } from "react";
import {UserState} from "./types";
import {safePost} from "./ajax_utils";
import { LoggedInUserState } from "./types";
import {Link, Navigate} from "react-router-dom";

type Props = {
    user_state: UserState,
    reloadUserState: () => void,
    clearLanguage: () => void,
    element: (user_state: LoggedInUserState) => React.ReactNode,
}

type State = {
}

export default class LoggedInPage extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
        };
    }

    logOut() {
        safePost("/admin/logout/", {}).then(() => this.props.reloadUserState())
    }


    render() {
        if (this.props.user_state.user === null) {
            return <Navigate to="/"/>;
        }

        const user_state: LoggedInUserState = {
            user: this.props.user_state.user,
            current_language: this.props.user_state.current_language,
        };

        return <>
            <div className="col-12 header">
                <div className="row">
                    <div className="col-2" style={{textAlign: "left"}}>
                        {user_state.current_language ? (
                            `Learning ${user_state.current_language.name}`
                        ) : null}
                    </div>
                    <div className="col-2" style={{textAlign: "left"}}>
                        {this.props.user_state.current_language ? (
                            <div className="button" onClick={() => this.props.clearLanguage()}>
                                Switch language
                            </div>
                        ) : null}
                    </div>
                    <div className="col-4" style={{textAlign: "center"}}>
                        <Link to="/" className="purple">
                            Membaca
                        </Link>
                    </div>
                    <div className="col-2" style={{textAlign: "center"}}>
                        {user_state.user.username}
                    </div>
                    <div className="col-2" style={{textAlign: "right"}}>
                        <div className="button" onClick={() => this.logOut()}>
                            Log out
                        </div>
                    </div>
                </div>
            </div>
            {this.props.element(user_state)}
        </>;
    }
}
