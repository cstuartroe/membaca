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
                            <h2>
                                Learning {user_state.current_language.name}
                            </h2>
                        ) : null}
                    </div>
                    <div className="col-2" style={{textAlign: "left"}}>
                        {this.props.user_state.current_language ? (
                            <Link to="/choose_language">
                                <div className="big button">
                                    Switch language
                                </div>
                            </Link>
                        ) : null}
                    </div>
                    <div className="col-4" style={{textAlign: "center"}}>
                        <Link to="/">
                            <h2 className="purple">
                                Membaca
                            </h2>
                        </Link>
                    </div>
                    <div className="col-2" style={{textAlign: "center"}}>
                        <h2>
                            {user_state.user.username}
                        </h2>
                    </div>
                    <div className="col-2" style={{textAlign: "right"}}>
                        <div className="big button" onClick={() => this.logOut()}>
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
