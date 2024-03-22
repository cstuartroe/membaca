import React, { Component } from "react";
import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";

import "../static/scss/main.scss";
import { UserState } from "./types";
import LanguageChooser from "./LanguageChooser";
import Home from "./Home";

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

        const router = createBrowserRouter([
            {
                path: "/",
                element: <Home user_state={this.state.user_state}/>
            },
            {
                path: "/choose_language",
                element: <LanguageChooser
                    user_state={this.state.user_state}
                    reloadUserState={() => this.reloadUserState()}
                />,
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
