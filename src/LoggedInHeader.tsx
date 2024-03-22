import React, { Component } from "react";
import {UserState} from "./types";
import {safePost} from "./ajax_utils";

type Props = {
    user_state: UserState,
    reloadUserState: () => void,
    clearLanguage: () => void,
}

type State = {
}

export default class LoggedInHeader extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
        };
    }

    logOut() {
        safePost("/admin/logout/", {}).then(() => this.props.reloadUserState())
    }


    render() {
        return (
            <div className="col-12 header">
                <div className="row">
                    <div className="col-3" style={{textAlign: "left"}}>
                        {this.props.user_state.current_language ? (
                            `Learning ${this.props.user_state.current_language.name}`
                        ) : null}
                    </div>
                    <div className="col-3" style={{textAlign: "left"}}>
                        {this.props.user_state.current_language ? (
                            <div className="button" onClick={() => this.props.clearLanguage()}>
                                Switch language
                            </div>
                        ) : null}
                    </div>
                    <div className="col-3" style={{textAlign: "center"}}>
                        {this.props.user_state.user ? (
                            this.props.user_state.user.username
                        ) : null}
                    </div>
                    <div className="col-3" style={{textAlign: "right"}}>
                        {this.props.user_state.user ? (
                            <div className="button" onClick={() => this.logOut()}>
                                Log out
                            </div>
                        ) : null}
                    </div>
                </div>
            </div>
        );
    }
}
