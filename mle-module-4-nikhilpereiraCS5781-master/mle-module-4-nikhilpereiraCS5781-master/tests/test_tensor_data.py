import minitorch
from hypothesis import given
from hypothesis.strategies import data
from .strategies import tensor_data, indices
import pytest
from numpy import array, array_equal

# ## Tasks 2.1

# Check basic properties of layout and strides.


@pytest.mark.task2_1
def test_layout():
    "Test basis properties of layout and strides"
    data = [0] * 3 * 5
    tensor_data = minitorch.TensorData(data, (3, 5), (5, 1))

    assert tensor_data.is_contiguous()
    assert tensor_data.shape == (3, 5)
    assert tensor_data.index((1, 0)) == 5
    assert tensor_data.index((1, 2)) == 7

    tensor_data = minitorch.TensorData(data, (5, 3), (1, 5))
    assert tensor_data.shape == (5, 3)
    assert not tensor_data.is_contiguous()

    data = [0] * 4 * 2 * 2
    tensor_data = minitorch.TensorData(data, (4, 2, 2))
    assert tensor_data.strides == (4, 2, 1)


@pytest.mark.xfail
def test_layout_bad():
    "Test basis properties of layout and strides"
    data = [0] * 3 * 5
    minitorch.TensorData(data, (3, 5), (6,))


@pytest.mark.task2_1
@given(tensor_data())
def test_enumeration(tensor_data):
    "Test enumeration of tensor_datas."
    indices = list(tensor_data.indices())

    # Check that enough positions are enumerated.
    assert len(indices) == tensor_data.size

    # Check that enough positions are enumerated only once.
    assert len(set(tensor_data.indices())) == len(indices)

    # Check that all indices are within the shape.
    for ind in tensor_data.indices():
        for i, p in enumerate(ind):
            assert p >= 0 and p < tensor_data.shape[i]


@pytest.mark.task2_1
@given(tensor_data())
def test_index(tensor_data):
    "Test enumeration of tensor_data."
    # Check that all indices are within the size.
    for ind in tensor_data.indices():
        pos = tensor_data.index(ind)
        assert pos >= 0 and pos < tensor_data.size

    base = [0] * tensor_data.dims
    with pytest.raises(minitorch.IndexingError):
        base[0] = -1
        tensor_data.index(tuple(base))

    if tensor_data.dims > 1:
        with pytest.raises(minitorch.IndexingError):
            base = [0] * (tensor_data.dims - 1)
            tensor_data.index(tuple(base))


@pytest.mark.task2_1
@given(data())
def test_permute(data):
    td = data.draw(tensor_data())
    ind = data.draw(indices(td))
    td_rev = td.permute(*list(reversed(range(td.dims))))
    assert td.index(ind) == td_rev.index(tuple(reversed(ind)))

    td2 = td_rev.permute(*list(reversed(range(td_rev.dims))))
    assert td.index(ind) == td2.index(ind)


# ## Tasks 2.2

# Check basic properties of broadcasting.


@pytest.mark.task2_2
def test_shape_broadcast():
    c = minitorch.shape_broadcast((1,), (5, 5))
    assert c == (5, 5)

    c = minitorch.shape_broadcast((5, 5), (1,))
    assert c == (5, 5)

    c = minitorch.shape_broadcast((1, 5, 5), (5, 5))
    assert c == (1, 5, 5)

    c = minitorch.shape_broadcast((5, 1, 5, 1), (1, 5, 1, 5))
    assert c == (5, 5, 5, 5)

    with pytest.raises(minitorch.IndexingError):
        c = minitorch.shape_broadcast((5, 7, 5, 1), (1, 5, 1, 5))
        print(c)

    with pytest.raises(minitorch.IndexingError):
        c = minitorch.shape_broadcast((5, 2), (5,))
        print(c)

    c = minitorch.shape_broadcast((2, 5), (5,))
    assert c == (2, 5)


@pytest.mark.task2_2
def test_broadcast_index():
    out_index = array([0, 0])

    def _broadcast_index(big_index):
        return minitorch.broadcast_index(
            big_index=big_index,
            big_shape=array([3, 2]),
            shape=array([3, 1]),
            out_index=out_index,
        )

    for big_index, expected_out_index in (
        ([0, 0], [0, 0]),
        ([0, 1], [0, 0]),
        ([1, 0], [1, 0]),
        ([1, 1], [1, 0]),
        ([2, 0], [2, 0]),
        ([2, 1], [2, 0]),
    ):
        _broadcast_index(big_index=array(big_index))
        assert array_equal(out_index, array(expected_out_index))


@pytest.mark.task2_2
def test_broadcast_index_constant():
    out_index = array([0])

    def _broadcast_index(big_index):
        return minitorch.broadcast_index(
            big_index=big_index,
            big_shape=array([3, 2]),
            shape=array([1]),
            out_index=out_index,
        )

    expected_out_index = array([0])
    for big_index in ([0, 0, 0], [0, 0, 1], [0, 0, 2], [1, 0, 0], [1, 0, 1], [1, 0, 2]):
        _broadcast_index(big_index=array(big_index))
        assert array_equal(out_index, expected_out_index)


@pytest.mark.task2_2
def test_broadcast_index_smaller():
    "Tests broadcast mapping between higher and lower dim tensors"
    out_index = array([-1, -1])

    def _broadcast_index(big_index):
        return minitorch.broadcast_index(
            big_index=big_index,
            big_shape=array([2, 2, 3]),
            shape=array([2, 1]),
            out_index=out_index,
        )

    for big_index, expected_out_index in (
        ([0, 0, 0], [0, 0]),
        ([0, 0, 1], [0, 0]),
        ([0, 0, 2], [0, 0]),
        ([0, 1, 0], [1, 0]),
        ([0, 1, 1], [1, 0]),
        ([0, 1, 2], [1, 0]),
        ([1, 0, 0], [0, 0]),
        ([1, 0, 1], [0, 0]),
        ([1, 0, 2], [0, 0]),
        ([1, 1, 0], [1, 0]),
        ([1, 1, 1], [1, 0]),
        ([1, 1, 2], [1, 0]),
    ):
        _broadcast_index(big_index=array(big_index))
        assert array_equal(out_index, expected_out_index)


@given(tensor_data())
def test_string(tensor_data):
    tensor_data.to_string()
