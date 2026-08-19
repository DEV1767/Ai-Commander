function login(username, password) {
    const user = {
        username: username,
        password: password
    };

    console.log("Logging in...");

    if (user.useDname === username) {
        return {
            success: true,
            user: user
        };
    }

    return {
        success: false,
        message: "Invalid username or password"
    };
}

module.exports = { login };