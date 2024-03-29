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
    user_menu_expanded: boolean,
}

export default class LoggedInPage extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            user_menu_expanded: false,
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
                    <div className="col-4" style={{textAlign: "left"}}>
                        {user_state.current_language ? (
                            <Link to="/choose_language">
                                <div className="big button">
                                    Learning {user_state.current_language.name}
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
                    <div className="col-4" style={{textAlign: "center", position: "relative"}}>
                        <div className="big button"
                             onClick={() => this.setState({user_menu_expanded: !this.state.user_menu_expanded})}
                        >
                            {user_state.user.username}
                        </div>
                        {this.state.user_menu_expanded && (
                            <div className="user-menu">
                                {user_state.user.is_superuser && (
                                    <a href="/admin_powers">
                                        <div className="big button">
                                            Use your admin powers!
                                        </div>
                                    </a>
                                )}
                                <div className="big button" onClick={() => this.logOut()}>
                                    Log out
                                </div>
                            </div>
                        )}
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
