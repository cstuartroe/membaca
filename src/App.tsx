import React, { Component } from "react";
import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";

import "../static/scss/main.scss";
import {LoggedInUserState, UserState} from "./types";
import LanguageChooser from "./LanguageChooser";
import Home from "./Home";
import Dashboard from "./Dashboard";
import _LoggedInPage from "./LoggedInPage";
import AddDocument from "./AddDocument";

type AppState = {
    user_state?: UserState,
}

class App extends Component<{}, AppState> {
    constructor(props: {}) {
        super(props);
        this.state = {};
    }

    reloadUserState() {
        fetch("/api/current_user_state")
            .then(res => res.json())
            .then(data => this.setState({
                user_state: data,
            }))
    }

    componentDidMount() {
        this.reloadUserState();
    }

    render() {
        if (this.state.user_state === undefined) {
            return null;
        }

        const { user_state } = this.state;

        const LoggedInPage = (props: {element: (s: LoggedInUserState) => React.ReactNode}) => {
            return <_LoggedInPage
                user_state={user_state}
                reloadUserState={() => this.reloadUserState()}
                clearLanguage={() => this.setState({user_state: {...user_state, current_language: null}})}
                element={props.element}/>
        }

        const router = createBrowserRouter([
            {
                path: "/",
                element: <Home user_state={user_state}/>
            },
            {
                path: "/choose_language",
                element: <LoggedInPage element={(user_state) => (
                    <LanguageChooser
                        user_state={user_state}
                        reloadUserState={() => this.reloadUserState()}
                    />
                )}/>,
            },
            {
                path: "/dashboard",
                element: <LoggedInPage element={(user_state) => (
                    <Dashboard user_state={user_state}/>
                )}/>,
            },
            {
                path: "/add_document",
                element: <LoggedInPage element={(user_state) => (
                    <AddDocument user_state={user_state}/>
                )}/>
            },
        ]);

        return <div className="container-fluid">
            <div className="row">
                <RouterProvider router={router}/>
            </div>
        </div>
    }
}

export default App;
