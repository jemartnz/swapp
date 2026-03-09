export const initialStore = () => ({
	user: {},
	users: [],
	token: "",
	categories: []
});

export function storeReducer(store, action = {}) {
	switch (action.type) {
		case "SET_USER":
			return {...store,
				user: typeof action.payload === "object"
					? action.payload
					: store.user
				};
		case "SET_USERS":
			return {
				...store,
				users: Array.isArray(action.payload)
					? action.payload
					: store.users
			};
		case "SET_TOKEN":
			return {...store,
				token: typeof action.payload === "string"
					? action.payload
					: store.token
				};
		case "SET_CATEGORIES":
			return {
				...store,
				categories: Array.isArray(action.payload)
					? action.payload
					: store.categories
			};
		default:
			throw new Error("Unknown action type: " + action.type);
	}
};
