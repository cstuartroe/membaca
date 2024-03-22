import React, { Component } from "react";
import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";

import "../static/scss/main.scss";
import { Language } from "./models";
import LanguageChooser from "./LanguageChooser";

type AppState = {
    all_languages?: Language[],
    language?: Language,
}

class App extends Component<{}, AppState> {
    constructor(props: {}) {
        super(props);
        this.state = {};
    }

    componentDidMount() {
        fetch("/languages")
            .then(res => res.json())
            .then(data => this.setState({
                all_languages: data,
            }))
    }

    render() {
        const languages = this.state.all_languages

        if (languages === undefined) {
            return <p>Loading languages...</p>
        }

        const router = createBrowserRouter([
            {
                path: "/",
                element: <LanguageChooser choices={languages} choose={(language: Language) => {
                    this.setState({language})
                }}/>,
            },
        ]);

        return <div className="container-fluid">
            <div className="row">
                {this.state.language?.name}
                <RouterProvider router={router}/>
            </div>
        </div>
    }
}

export default App;
