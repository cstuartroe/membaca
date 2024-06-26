import React, { Component } from "react";
import {
    createBrowserRouter, Navigate,
    RouterProvider,
} from "react-router-dom";

import "../static/scss/main.scss";
import {LoggedInUserState} from "./LoggedInPage";
import LanguageChooser from "./LanguageChooser";
import Dashboard from "./dashboard/Dashboard";
import LoggedInPage from "./LoggedInPage";
import AddDocument from "./AddDocument";
import Document from "./document/Document";
import Collections from "./Collections";
import {Language, User} from "./models";
import AdminPowers from "./AdminPowers";
import Cards from "./flashcards/Cards";
import Collection from "./Collection";
import IndonesianEPicker from "./IndonesianEPicker";
import LoggedOutHome from "./LoggedOutHome";
import DutchGenderPicker from "./DutchGenderPicker";
import MetadataCards from "./flashcards/MetadataCards";

type AppState = {
    user_state?: {
        user: User | null,
        current_language: Language | null,
    },
}

class App extends Component<{}, AppState> {
    constructor(props: {}) {
        super(props);
        this.state = {};
    }

    reloadUserState() {
        return fetch("/api/current_user_state")
            .then(res => res.json())
            .then(data => this.setState({
                user_state: data,
            }))
    }

    componentDidMount() {
        this.reloadUserState();
    }

    loggedOutPage() {
        const loggedOutRoutes = [
            {
                path: "/",
                element: <LoggedOutHome/>,
            },
            {
                path: "*",
                element: <Navigate to="/"/>,
            },
        ];

        return <RouterProvider router={createBrowserRouter(loggedOutRoutes)}/>;
    }

    noLanguageChosenRoutes() {
        return [
            {
                path: "/choose_language",
                element: <LanguageChooser reloadUserState={() => this.reloadUserState()}/>,
            },
            {
                path: "*",
                element: <Navigate to={`/choose_language?next=${window.location.pathname}`}/>
            },
        ];
    }

    languageChosenRoutes(user: User, current_language: Language) {
        return [
            {
                path: "/choose_language",
                element: <LanguageChooser reloadUserState={() => this.reloadUserState()}/>,
            },
            {
                path: "/dashboard",
                element: <Dashboard is_superuser={user.is_superuser} current_language={current_language}/>,
            },
            {
                path: "/add_document",
                element: <AddDocument language={current_language}/>,
            },
            {
                path: "/document/:documentId",
                element: <Document language={current_language}/>,
            },
            {
                path: "/collections",
                element: <Collections language={current_language}/>,
            },
            {
                path: "/collection/:collectionId",
                element: <Collection/>,
            },
            {
                path: "/admin_powers",
                element: <AdminPowers user={user}/>
            },
            {
                path: "/cards/new",
                element: <Cards user={user} language={current_language} new={true}/>
            },
            {
                path: "/cards/review",
                element: <Cards user={user} language={current_language} new={false}/>
            },
            {
                path: "/indonesian_e",
                element: <IndonesianEPicker/>
            },
            {
                path: "/dutch_gender",
                element: <DutchGenderPicker/>
            },
            {
                path: "/metadata_cards/new",
                element: <MetadataCards user={user} language={current_language} new={true}/>
            },
            {
                path: "/metadata_cards/review",
                element: <MetadataCards user={user} language={current_language} new={false}/>
            },
            {
                path: "*",
                element: <Navigate to="/dashboard"/>
            },
        ];
    }

    loggedInRoutes(user_state: LoggedInUserState) {
        const { user, current_language } = user_state;

        if (current_language === null) {
            return this.noLanguageChosenRoutes();
        } else {
            return this.languageChosenRoutes(user, current_language);
        }
    }

    loggedInPage(user_state: LoggedInUserState) {
        const routesWithoutWrapping = this.loggedInRoutes(user_state);
        const routesWithWrapping = routesWithoutWrapping.map(({path, element}) => (
            {
                path,
                element: (
                    <LoggedInPage
                        user_state={user_state}
                        reloadUserState={() => this.reloadUserState()}
                        clearLanguage={() => this.setState({user_state: {...user_state, current_language: null}})}>
                        {element}
                    </LoggedInPage>
                ),
            }
        ))

        return <RouterProvider router={createBrowserRouter(routesWithWrapping)}/>;
    }

    render() {
        if (this.state.user_state === undefined) {
            return null;
        }

        const { user, current_language } = this.state.user_state;

        if (user === null) {
            return this.loggedOutPage();
        } else {
            return this.loggedInPage({user, current_language})
        }
    }
}

export default App;
