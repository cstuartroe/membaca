import React, { Component } from "react";
import {safePost} from "./ajax_utils";
import {Link} from "react-router-dom";
import {Language, User} from "./models";

export type LoggedInUserState = {
    user: User,
    current_language: Language | null,
}

type Props = {
    user_state: LoggedInUserState,
    reloadUserState: () => void,
    clearLanguage: () => void,
    children?: React.ReactNode,
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

    header() {
        const { user_state } = this.props;

        return (
            <div className="col-12 header">
                <div className="row">
                    <div className="col-2" style={{textAlign: "left"}}>
                        {user_state.current_language ? (
                            `Learning ${user_state.current_language.name}`
                        ) : null}
                    </div>
                    <div className="col-2" style={{textAlign: "left"}}>
                        {this.props.user_state.current_language ? (
                            <Link to="/choose_language">
                                <div className="button">
                                    Switch language
                                </div>
                            </Link>
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
        );
    }


    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    {this.header()}
                    {this.props.children}
                </div>
            </div>
        );
    }
}
