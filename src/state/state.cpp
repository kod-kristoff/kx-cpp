#include "kx/state/state.hpp"

namespace kx::state
{
    State::~State()
    {}

    /* virtual */
    void State::update(Time dt)
    {}

    /* virtual */
    void State::draw(Renderer * renderer) const
    {}

    /* virtual */
    void State::on_enter()
    {}

    /* virtual */
    void State::on_leave()
    {}
}
